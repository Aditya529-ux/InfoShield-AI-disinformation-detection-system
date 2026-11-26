"""
Model Training & Persistence Pipeline for InfoShield.
Trains on LIAR and PolitiFact datasets, computes test metrics,
and serializes the model to disk so it remembers its training for eternity.
"""

from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Dict, Any

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.utils.class_weight import compute_sample_weight

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.dataset import get_all_splits

MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODELS_DIR / "infoshield_active.joblib"
REGISTRY_FILE = MODELS_DIR / "registry.json"


def train_and_save_model(include_politifact: bool = True) -> Dict[str, Any]:
    """
    Trains the TF-IDF + SGDClassifier model on the combined dataset.
    Computes evaluation metrics on the held-out test split.
    Saves the trained pipeline to disk and updates registry.json.
    """
    print("Loading dataset splits...")
    train_df, valid_df, test_df = get_all_splits(include_politifact=include_politifact)
    print(f"Total training samples: {len(train_df)}, Test samples: {len(test_df)}")

    # 1. Feature Extraction: TF-IDF
    print("Vectorizing text with TF-IDF...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=30000,
        sublinear_tf=True,
        strip_accents="unicode",
        lowercase=True,
    )
    X_train = vectorizer.fit_transform(train_df["statement"])
    y_train = train_df["label"].to_numpy()

    X_test = vectorizer.transform(test_df["statement"])
    y_test = test_df["label"].to_numpy()

    # 2. Balanced sample weights for initial training
    sample_weights = compute_sample_weight("balanced", y_train)

    # 3. Model: SGDClassifier with log_loss (Logistic Regression)
    # Allows calibrated probabilities, feature coefficients, and incremental online learning (partial_fit)
    print("Training SGDClassifier (Logistic Regression)...")
    classifier = SGDClassifier(
        loss="log_loss",
        penalty="l2",
        alpha=1e-5,
        max_iter=2000,
        tol=1e-4,
        random_state=42
    )
    classifier.fit(X_train, y_train, sample_weight=sample_weights)

    # 4. Evaluation on test set
    print("Evaluating on held-out test split...")
    test_preds = classifier.predict(X_test)
    test_acc = accuracy_score(y_test, test_preds)
    prec = precision_score(y_test, test_preds, pos_label=1)
    rec = recall_score(y_test, test_preds, pos_label=1)
    f1 = f1_score(y_test, test_preds, pos_label=1)
    cm = confusion_matrix(y_test, test_preds).tolist()
    report = classification_report(y_test, test_preds, output_dict=True)

    print(f"Test Accuracy: {test_acc:.4f} | Fake F1: {f1:.4f} | Fake Precision: {prec:.4f}")

    # 5. Persist Model Bundle to Disk for Eternity
    model_bundle = {
        "vectorizer": vectorizer,
        "classifier": classifier,
        "classes": classifier.classes_.tolist(),
        "created_at": datetime.now().isoformat(),
        "total_train_samples": len(train_df),
        "feedback_samples_learned": 0,
        "version": "1.0.0"
    }
    joblib.dump(model_bundle, MODEL_FILE)
    print(f"Model successfully saved to {MODEL_FILE}")

    # 6. Save Registry Metadata
    registry_data = {
        "model_name": "InfoShield-SGD-LogLoss",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "metrics": {
            "test_accuracy": round(float(test_acc), 4),
            "fake_precision": round(float(prec), 4),
            "fake_recall": round(float(rec), 4),
            "fake_f1": round(float(f1), 4),
            "confusion_matrix": cm,
            "detailed_report": report
        },
        "stats": {
            "base_training_samples": len(train_df),
            "test_samples": len(test_df),
            "vocabulary_size": len(vectorizer.vocabulary_),
            "feedback_samples_incorporated": 0,
            "disk_size_kb": round(MODEL_FILE.stat().st_size / 1024, 2) if MODEL_FILE.exists() else 0
        }
    }

    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, indent=2)

    return registry_data


if __name__ == "__main__":
    train_and_save_model(include_politifact=True)
