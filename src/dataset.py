"""
Dataset loading and preprocessing module for InfoShield.
Loads LIAR dataset splits and optionally PolitiFact JSON data.
"""

import json
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple
import pandas as pd

DATASETS_DIR = Path(__file__).resolve().parent.parent / "datasets"

# Label mapping
# Reliable: true, mostly-true -> 0
# Fake / Misleading: half-true, barely-true, false, pants-fire, mostly-false -> 1
LABEL_MAP_BINARY = {
    "true": 0,
    "mostly-true": 0,
    "half-true": 1,
    "barely-true": 1,
    "false": 1,
    "pants-fire": 1,
    "mostly-false": 1,
}

LABEL_NAMES_BINARY = {
    0: "Reliable / Credible",
    1: "Fake / Misleading",
}


def clean_text(text: str) -> str:
    """Basic text cleanup suitable for NLP text classification."""
    if not isinstance(text, str):
        return ""
    # Normalize whitespaces and clean quotation marks
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_liar_split(split: str = "train") -> pd.DataFrame:
    """
    Load a single TSV split from the LIAR dataset.
    split: 'train', 'valid', or 'test'
    """
    file_path = DATASETS_DIR / f"{split}.tsv"
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset split not found: {file_path}")

    # Column 0: id, Column 1: label, Column 2: statement, Column 3: subject, Column 4: speaker...
    df = pd.read_csv(file_path, sep="\t", header=None, quoting=3, on_bad_lines="skip")
    df = df.rename(columns={
        0: "id",
        1: "original_label",
        2: "statement",
        3: "subject",
        4: "speaker",
        5: "job_title",
        6: "state",
        7: "party",
    })

    df["statement"] = df["statement"].astype(str).apply(clean_text)
    df["label"] = df["original_label"].str.strip().str.lower().map(LABEL_MAP_BINARY)
    # Drop records where label mapping is NaN or text is empty
    df = df.dropna(subset=["label", "statement"])
    df["label"] = df["label"].astype(int)
    return df[["id", "statement", "original_label", "label", "speaker", "party"]].copy()


def load_politifact_json() -> pd.DataFrame:
    """Load additional PolitiFact records if available."""
    json_path = DATASETS_DIR / "politifact_factcheck_data.json"
    if not json_path.exists():
        return pd.DataFrame()

    records = []
    with open(json_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            try:
                item = json.loads(line)
                verdict = str(item.get("verdict", "")).strip().lower()
                stmt = clean_text(item.get("statement", ""))
                if verdict in LABEL_MAP_BINARY and stmt:
                    records.append({
                        "id": f"pf_{idx}",
                        "statement": stmt,
                        "original_label": verdict,
                        "label": LABEL_MAP_BINARY[verdict],
                        "speaker": item.get("statement_originator", "Unknown"),
                        "party": "Unknown"
                    })
            except Exception:
                continue

    return pd.DataFrame(records)


def get_all_splits(include_politifact: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns train_df, valid_df, test_df."""
    train_df = load_liar_split("train")
    valid_df = load_liar_split("valid")
    test_df = load_liar_split("test")

    if include_politifact:
        extra_df = load_politifact_json()
        if not extra_df.empty:
            # Combine into train set
            train_df = pd.concat([train_df, extra_df], ignore_index=True)

    return train_df, valid_df, test_df


if __name__ == "__main__":
    tr, va, te = get_all_splits(include_politifact=False)
    print(f"LIAR Splits Loaded - Train: {len(tr)}, Valid: {len(va)}, Test: {len(te)}")
    print("Train label distribution:\n", tr["label"].value_counts())
