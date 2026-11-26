"""
Explainability Engine (XAI) for InfoShield.
Performs token-level feature attribution and generates structured plain-English explanations.
"""

from typing import Dict, List, Tuple, Any
import numpy as np


class TextExplainer:
    def __init__(self, vectorizer, classifier):
        self.vectorizer = vectorizer
        self.classifier = classifier
        self.feature_names = vectorizer.get_feature_names_out()
        self.weights = classifier.coef_[0]
        self.intercept = float(classifier.intercept_[0])

    def explain(self, text: str, pred_label: int, confidence: float) -> Dict[str, Any]:
        """
        Calculates token attribution and structured reasoning for the input text.
        """
        x_vec = self.vectorizer.transform([text])
        non_zero_indices = x_vec.nonzero()[1]

        contributions = []
        for idx in non_zero_indices:
            term = self.feature_names[idx]
            tfidf_val = x_vec[0, idx]
            weight = self.weights[idx]
            impact = float(weight * tfidf_val)
            contributions.append({
                "term": term,
                "impact": round(impact, 4),
                "weight": round(float(weight), 4),
                "tfidf": round(float(tfidf_val), 4),
                # Positive pushes to Fake (1), Negative pushes to Reliable (0)
                "category": "fake_signal" if impact > 0 else "reliable_signal",
                "abs_impact": abs(impact)
            })

        # Sort by absolute impact
        contributions.sort(key=lambda item: item["abs_impact"], reverse=True)

        fake_signals = [c for c in contributions if c["impact"] > 0][:8]
        reliable_signals = [c for c in contributions if c["impact"] < 0][:8]

        # Generate structured plain-English rationale
        rationale = self._generate_rationale(text, pred_label, confidence, fake_signals, reliable_signals)

        return {
            "prediction": pred_label,
            "verdict": "Fake / Misleading" if pred_label == 1 else "Reliable / Credible",
            "confidence": round(float(confidence), 4),
            "intercept": round(self.intercept, 4),
            "top_fake_contributors": fake_signals,
            "top_reliable_contributors": reliable_signals,
            "all_token_attributions": contributions[:20],
            "rationale": rationale
        }

    def _generate_rationale(
        self,
        text: str,
        pred_label: int,
        confidence: float,
        fake_signals: List[Dict],
        reliable_signals: List[Dict]
    ) -> str:
        conf_pct = f"{confidence * 100:.1f}%"
        fake_words = [f"'{c['term']}'" for c in fake_signals[:4]]
        reliable_words = [f"'{c['term']}'" for c in reliable_signals[:4]]

        if pred_label == 1:
            if fake_words:
                reason = (
                    f"Classified as Likely Disinformation / Fake with {conf_pct} confidence. "
                    f"The decision is primarily driven by terms like {', '.join(fake_words)}, which frequently "
                    f"appear in unverified or debunked claims in fact-checking archives. "
                )
            else:
                reason = (
                    f"Classified as Likely Disinformation / Fake with {conf_pct} confidence based on overall "
                    f"stylistic and vocabulary patterns matching known misinformation instances."
                )
            if reliable_words:
                reason += f" Counter-balancing terms like {', '.join(reliable_words)} were present, but insufficient to offset the disinformation signals."
            return reason
        else:
            if reliable_words:
                reason = (
                    f"Classified as Reliable / Credible with {conf_pct} confidence. "
                    f"The statement incorporates verifiable markers and institutional context words such as {', '.join(reliable_words)}, "
                    f"consistent with credible factual reporting."
                )
            else:
                reason = (
                    f"Classified as Reliable / Credible with {conf_pct} confidence based on neutral language "
                    f"and an absence of sensationalist or speculative disinformation markers."
                )
            if fake_words:
                reason += f" Note that terms like {', '.join(fake_words)} warranted caution, but the net context supports credibility."
            return reason
