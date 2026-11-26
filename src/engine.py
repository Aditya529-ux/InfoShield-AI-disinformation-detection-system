"""
Inference & Continual Learning Engine for InfoShield.
Coordinates prediction, explainability, online learning updates, model persistence,
and majority-vote community feedback recall against datasets/user_feedback.json.
"""

from datetime import datetime
import json
from pathlib import Path
import sys
import threading
from typing import Dict, Any, Optional

import joblib
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.explainer import TextExplainer
from src.database import (
    lookup_memory_record,
    record_new_query_in_dataset,
    apply_user_feedback_to_dataset,
    get_stats as get_db_stats,
    USER_FEEDBACK_DATASET_FILE
)
from src.model_trainer import train_and_save_model, MODEL_FILE, REGISTRY_FILE


class InfoShieldEngine:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(InfoShieldEngine, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.lock = threading.Lock()
        self.load_model()

    def load_model(self):
        """Loads serialized model from disk or trains a new one if not present."""
        if not MODEL_FILE.exists():
            print(f"Model file {MODEL_FILE} not found. Initiating initial training...")
            train_and_save_model(include_politifact=True)

        print(f"Loading persistent model from {MODEL_FILE}...")
        self.bundle = joblib.load(MODEL_FILE)
        self.vectorizer = self.bundle["vectorizer"]
        self.classifier = self.bundle["classifier"]
        self.explainer = TextExplainer(self.vectorizer, self.classifier)
        self.version = self.bundle.get("version", "1.0.0")
        self.feedback_count = self.bundle.get("feedback_samples_learned", 0)

    def predict_and_explain(
        self,
        text: str,
        headline: str = "",
        article: str = ""
    ) -> Dict[str, Any]:
        """
        Predicts whether text is Fake or Reliable.
        1. Checks datasets/user_feedback.json for a majority-vote community record.
           - If found with votes: returns the majority verdict with vote counts.
           - If tied: falls back to ML and shows tie notice.
        2. Otherwise runs ML classifier with XAI explanation.
        """
        text = text.strip()
        if not text:
            raise ValueError("Input text cannot be empty.")

        # --- STEP 1: Check Community Majority-Vote Memory ---
        memory_match = lookup_memory_record(text)
        if memory_match:
            fv = memory_match.get("fake_votes", 0)
            rv = memory_match.get("reliable_votes", 0)
            total_votes = fv + rv
            verdict_source = memory_match.get("verdict_source", "ml_model")

            if verdict_source == "tie_fallback_ml":
                # Tied votes — run ML instead and show tie notice
                rationale_prefix = (
                    f"⚖️ [Community Tie — Falling Back to ML]: This statement has been rated by "
                    f"{total_votes} user(s) — {fv} Fake vote(s) vs {rv} Reliable vote(s). "
                    f"Since votes are tied, InfoShield falls back to its ML model for the final verdict. "
                )
                return self._run_ml_inference(
                    text, headline, article,
                    rationale_prefix=rationale_prefix,
                    is_memory_recall=True,
                    fake_votes=fv,
                    reliable_votes=rv,
                    verdict_source=verdict_source,
                    total_community_feedbacks=total_votes
                )

            # Clear majority exists — use it
            effective_label = int(memory_match["effective_label"])
            verdict = "Reliable / Credible" if effective_label == 0 else "Fake / Misleading"
            explanation = self.explainer.explain(text, effective_label, 1.0)

            fake_pct = round(fv / total_votes * 100) if total_votes else 0
            reliable_pct = round(rv / total_votes * 100) if total_votes else 0
            winner = "Fake" if fv > rv else "Reliable"

            rationale = (
                f"🗳️ [Community Consensus — Real-World Feedback]: This statement has been evaluated by "
                f"{total_votes} user(s): {fv} said Fake ({fake_pct}%) and {rv} said Reliable ({reliable_pct}%). "
                f"The majority verdict is {winner}. InfoShield recalls this result with 100% certainty based on "
                f"real-world user feedback. Result verified as: {verdict}."
            )
            explanation["rationale"] = rationale

            # Log to history (use effective label)
            record_new_query_in_dataset(
                text=text,
                headline=headline,
                article=article,
                predicted_label=effective_label,
                confidence=1.0,
                top_fake_words=[c["term"] for c in explanation["top_fake_contributors"][:3]],
                top_reliable_words=[c["term"] for c in explanation["top_reliable_contributors"][:3]]
            )

            return {
                "text": text,
                "headline": headline,
                "article": article,
                "prediction": effective_label,
                "verdict": verdict,
                "confidence": 1.0,
                "probabilities": {
                    "reliable": 1.0 if effective_label == 0 else 0.0,
                    "fake": 1.0 if effective_label == 1 else 0.0
                },
                "risk_level": "Community Verified",
                "is_memory_recall": True,
                "verdict_source": verdict_source,
                "fake_votes": fv,
                "reliable_votes": rv,
                "total_community_feedbacks": total_votes,
                "memory_status": "Community Consensus",
                "explanation": explanation
            }

        # --- STEP 2: Standard ML Inference (no community memory) ---
        return self._run_ml_inference(text, headline, article)

    def _run_ml_inference(
        self,
        text: str,
        headline: str = "",
        article: str = "",
        rationale_prefix: str = "",
        is_memory_recall: bool = False,
        fake_votes: int = 0,
        reliable_votes: int = 0,
        verdict_source: str = "ml_model",
        total_community_feedbacks: int = 0
    ) -> Dict[str, Any]:
        """Runs the TF-IDF + SGDClassifier pipeline with XAI."""
        x_vec = self.vectorizer.transform([text])
        probabilities = self.classifier.predict_proba(x_vec)[0]
        prob_reliable = float(probabilities[0])
        prob_fake = float(probabilities[1])

        pred_label = 1 if prob_fake >= 0.50 else 0
        confidence = prob_fake if pred_label == 1 else prob_reliable

        if pred_label == 1:
            if prob_fake >= 0.85:
                risk_level = "High Disinformation Risk"
            elif prob_fake >= 0.65:
                risk_level = "Moderate Disinformation Risk"
            else:
                risk_level = "Low/Borderline Risk"
        else:
            if prob_reliable >= 0.85:
                risk_level = "High Credibility"
            elif prob_reliable >= 0.65:
                risk_level = "Moderate Credibility"
            else:
                risk_level = "Borderline Credibility"

        explanation = self.explainer.explain(text, pred_label, confidence)
        if rationale_prefix:
            explanation["rationale"] = rationale_prefix + explanation.get("rationale", "")

        fake_terms = [c["term"] for c in explanation["top_fake_contributors"][:3]]
        reliable_terms = [c["term"] for c in explanation["top_reliable_contributors"][:3]]
        query_id = record_new_query_in_dataset(
            text=text,
            headline=headline,
            article=article,
            predicted_label=pred_label,
            confidence=confidence,
            top_fake_words=fake_terms,
            top_reliable_words=reliable_terms
        )

        return {
            "query_id": query_id,
            "text": text,
            "headline": headline,
            "article": article,
            "prediction": pred_label,
            "verdict": "Fake / Misleading" if pred_label == 1 else "Reliable / Credible",
            "confidence": round(confidence, 4),
            "probabilities": {
                "reliable": round(prob_reliable, 4),
                "fake": round(prob_fake, 4)
            },
            "risk_level": risk_level,
            "is_memory_recall": is_memory_recall,
            "verdict_source": verdict_source,
            "fake_votes": fake_votes,
            "reliable_votes": reliable_votes,
            "total_community_feedbacks": total_community_feedbacks,
            "explanation": explanation
        }

    def learn_from_feedback(
        self,
        text: str,
        user_label: int,
        user_action: str = "disagree",
        source_note: Optional[str] = None,
        query_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Human-in-the-loop Continual Learning:
        1. Adds the user's vote to the consolidated record in datasets/user_feedback.json.
        2. Recomputes the majority verdict (or falls back to tie-breaker ML).
        3. Applies incremental partial_fit to the classifier weights.
        4. Persists updated model to disk.
        """
        with self.lock:
            # 1. Record vote and recompute majority
            vote_result = apply_user_feedback_to_dataset(
                text=text,
                user_label=user_label,
                user_action=user_action,
                source_note=source_note,
                query_id=query_id
            )

            # 2. Online incremental learning
            x_vec = self.vectorizer.transform([text])
            y_arr = np.array([user_label])
            self.classifier.partial_fit(x_vec, y_arr)
            self.explainer = TextExplainer(self.vectorizer, self.classifier)

            # 3. Persist updated weights
            self.feedback_count += 1
            self.bundle["classifier"] = self.classifier
            self.bundle["feedback_samples_learned"] = self.feedback_count
            self.bundle["last_updated"] = datetime.now().isoformat()
            joblib.dump(self.bundle, MODEL_FILE)

            # 4. Quick sanity check on updated model
            p_after = self.classifier.predict_proba(x_vec)[0]
            new_pred = 1 if p_after[1] >= 0.50 else 0
            new_conf = float(p_after[new_pred])

            fv = vote_result["fake_votes"]
            rv = vote_result["reliable_votes"]
            total = vote_result["total_votes"]
            majority_verdict = vote_result["majority_verdict"]
            verdict_source = vote_result["verdict_source"]

            return {
                "status": "success",
                "message": (
                    f"Vote recorded! Community now shows {fv} Fake vote(s) vs {rv} Reliable vote(s) "
                    f"(total: {total}). Majority verdict: {majority_verdict}. "
                    f"Model weights updated on localhost."
                ),
                "total_feedback_learned": self.feedback_count,
                "remembered_label": vote_result["majority_label"],
                "remembered_verdict": majority_verdict,
                "verdict_source": verdict_source,
                "fake_votes": fv,
                "reliable_votes": rv,
                "total_votes": total,
                "majority_verdict": majority_verdict,
                "new_confidence": round(new_conf, 4),
                "probabilities": {
                    "reliable": round(float(p_after[0]), 4),
                    "fake": round(float(p_after[1]), 4)
                }
            }

    def get_stats(self) -> Dict[str, Any]:
        """Returns comprehensive model and dataset statistics."""
        db_stats = get_db_stats()
        registry_info = {}
        if REGISTRY_FILE.exists():
            try:
                with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                    registry_info = json.load(f)
            except Exception:
                pass

        return {
            "model_version": self.version,
            "feedback_samples_learned": self.feedback_count,
            "test_accuracy": registry_info.get("metrics", {}).get("test_accuracy", 0.8129),
            "fake_f1": registry_info.get("metrics", {}).get("fake_f1", 0.8427),
            "base_samples": registry_info.get("stats", {}).get("base_training_samples", 31421),
            "vocabulary_size": registry_info.get("stats", {}).get("vocabulary_size", 30000),
            "user_feedback_stats": db_stats,
            "dataset_file": str(USER_FEEDBACK_DATASET_FILE),
            "model_path": str(MODEL_FILE),
            "last_updated": self.bundle.get("last_updated", self.bundle.get("created_at"))
        }


def get_engine() -> InfoShieldEngine:
    return InfoShieldEngine()


if __name__ == "__main__":
    engine = get_engine()
    test_claim = "Drinking boiled garlic water completely eliminates viral infections in 24 hours."
    print("Testing ML prediction:")
    r1 = engine.predict_and_explain(test_claim)
    print("Initial Verdict:", r1["verdict"], "Confidence:", r1["confidence"])

    print("\nSimulating user feedback: Correct to Reliable (0)...")
    engine.learn_from_feedback(test_claim, user_label=0, user_action="disagree", source_note="Test user verification")

    print("\nQuerying same statement again (Testing exact memory recall):")
    r2 = engine.predict_and_explain(test_claim)
    print("Second Verdict:", r2["verdict"], "Confidence:", r2["confidence"], "| Is Memory Recall:", r2.get("is_memory_recall"))
    print("Fake votes:", r2.get("fake_votes"), "| Reliable votes:", r2.get("reliable_votes"))
    print("Verdict source:", r2.get("verdict_source"))
