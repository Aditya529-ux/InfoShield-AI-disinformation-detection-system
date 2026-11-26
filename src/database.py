"""
Storage & User Feedback Dataset Management for InfoShield.
Manages datasets/user_feedback.json and SQLite database on localhost.
Supports majority-vote multi-user feedback and exact-match memory recall.
Each unique normalized_key gets ONE consolidated record with fake_votes / reliable_votes.
"""

from datetime import datetime
import json
from pathlib import Path
import re
import sqlite3
import threading
from typing import Dict, List, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)
USER_FEEDBACK_DATASET_FILE = DATASETS_DIR / "user_feedback.json"

STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = STORAGE_DIR / "feedback.db"

_file_lock = threading.Lock()


def normalize_key(text: str) -> str:
    """Normalizes text for robust exact/near-exact memory lookup."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _migrate_old_record(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Migrates a single-user (old-format) record to the majority-vote consolidated format."""
    if "fake_votes" in entry and "reliable_votes" in entry:
        return entry  # Already in new format

    # Determine what the old feedback said
    old_action = entry.get("user_action", "none")
    old_effective_label = entry.get("effective_label", entry.get("model_prediction", 0))
    old_feedback_status = entry.get("feedback_status", "assumed_accurate")
    model_pred = entry.get("model_prediction", old_effective_label)

    if old_feedback_status in ("user_corrected", "user_confirmed") and old_action != "none":
        # There was an explicit feedback — count it as one vote
        if old_effective_label == 1:
            fake_votes = 1
            reliable_votes = 0
        else:
            fake_votes = 0
            reliable_votes = 1
        majority_label = old_effective_label
        majority_verdict = "Fake / Misleading" if majority_label == 1 else "Reliable / Credible"
        verdict_source = "majority_user_vote"
        feedback_status = "community_consensus"
        individual_feedbacks = [{
            "user_action": old_action,
            "user_label": old_effective_label,
            "source_note": entry.get("source_note", "Migrated from single-user record"),
            "timestamp": entry.get("last_updated", entry.get("timestamp", datetime.now().isoformat()))
        }]
    else:
        fake_votes = 0
        reliable_votes = 0
        majority_label = model_pred
        majority_verdict = "Fake / Misleading" if majority_label == 1 else "Reliable / Credible"
        verdict_source = "ml_model"
        feedback_status = "assumed_accurate"
        individual_feedbacks = []

    pred_verdict = "Fake / Misleading" if model_pred == 1 else "Reliable / Credible"
    return {
        "normalized_key": entry.get("normalized_key", normalize_key(entry.get("text", ""))),
        "headline": entry.get("headline", ""),
        "article": entry.get("article", ""),
        "text": entry.get("text", ""),
        "first_seen": entry.get("timestamp", datetime.now().isoformat()),
        "last_updated": entry.get("last_updated", entry.get("timestamp", datetime.now().isoformat())),
        "model_prediction": model_pred,
        "model_confidence": entry.get("model_confidence", 0.0),
        "predicted_verdict": pred_verdict,
        "total_queries": 1,
        "fake_votes": fake_votes,
        "reliable_votes": reliable_votes,
        "majority_label": majority_label,
        "majority_verdict": majority_verdict,
        "effective_label": majority_label,
        "effective_verdict": majority_verdict,
        "verdict_source": verdict_source,
        "feedback_status": feedback_status,
        "individual_feedbacks": individual_feedbacks
    }


def load_user_feedback_dataset() -> List[Dict[str, Any]]:
    """Loads all records from datasets/user_feedback.json, migrating old-format records."""
    if not USER_FEEDBACK_DATASET_FILE.exists():
        return []
    with _file_lock:
        try:
            with open(USER_FEEDBACK_DATASET_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if not isinstance(raw, list):
                    return []
                migrated = []
                changed = False
                for rec in raw:
                    if "fake_votes" not in rec:
                        migrated.append(_migrate_old_record(rec))
                        changed = True
                    else:
                        migrated.append(rec)
                if changed:
                    # Write migrated data back (while still holding the lock)
                    with open(USER_FEEDBACK_DATASET_FILE, "w", encoding="utf-8") as wf:
                        json.dump(migrated, wf, indent=2, ensure_ascii=False)
                return migrated
        except Exception:
            return []


def save_user_feedback_dataset(records: List[Dict[str, Any]]):
    """Saves records to datasets/user_feedback.json atomically."""
    with _file_lock:
        with open(USER_FEEDBACK_DATASET_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                headline TEXT,
                article TEXT,
                predicted_label INTEGER NOT NULL,
                confidence REAL NOT NULL,
                user_label INTEGER NOT NULL,
                user_action TEXT NOT NULL,
                feedback_status TEXT NOT NULL DEFAULT 'assumed_accurate',
                source_note TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                applied_to_model INTEGER DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                headline TEXT,
                article TEXT,
                prediction INTEGER NOT NULL,
                confidence REAL NOT NULL,
                effective_verdict TEXT,
                feedback_status TEXT DEFAULT 'Assumed Accurate',
                top_fake_words TEXT,
                top_reliable_words TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Safe migration for tables that existed from earlier runs
        for table, col in [
            ("prediction_history", "headline TEXT"),
            ("prediction_history", "article TEXT"),
            ("prediction_history", "effective_verdict TEXT"),
            ("prediction_history", "feedback_status TEXT DEFAULT 'Assumed Accurate'"),
            ("feedbacks", "headline TEXT"),
            ("feedbacks", "article TEXT"),
            ("feedbacks", "feedback_status TEXT DEFAULT 'assumed_accurate'")
        ]:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass

        conn.commit()

    # Ensure datasets/user_feedback.json exists
    if not USER_FEEDBACK_DATASET_FILE.exists():
        save_user_feedback_dataset([])


def lookup_memory_record(text: str) -> Optional[Dict[str, Any]]:
    """
    Checks datasets/user_feedback.json for a previous verified entry.
    Returns the consolidated record ONLY if at least one explicit user vote exists.
    Returns None if the record was only seen by ML (no explicit feedback yet).
    """
    norm = normalize_key(text)
    if not norm or len(norm) < 10:
        return None

    dataset = load_user_feedback_dataset()
    for entry in dataset:
        if entry.get("normalized_key") == norm:
            # Only use memory recall if users have explicitly voted
            total_votes = entry.get("fake_votes", 0) + entry.get("reliable_votes", 0)
            if total_votes > 0:
                return entry
            return None  # Found but no user votes yet — let ML handle it
    return None


def _find_or_create_consolidated_record(
    dataset: List[Dict[str, Any]],
    norm: str,
    text: str,
    headline: str,
    article: str,
    predicted_label: int,
    confidence: float
) -> tuple:
    """
    Finds existing consolidated record for norm key, or creates a new one.
    Returns (record_dict, index_in_list_or_None).
    """
    for idx, entry in enumerate(dataset):
        if entry.get("normalized_key") == norm:
            return entry, idx

    pred_verdict = "Fake / Misleading" if predicted_label == 1 else "Reliable / Credible"
    new_record = {
        "normalized_key": norm,
        "headline": headline or "",
        "article": article or "",
        "text": text,
        "first_seen": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "model_prediction": predicted_label,
        "model_confidence": round(float(confidence), 4),
        "predicted_verdict": pred_verdict,
        "total_queries": 0,
        "fake_votes": 0,
        "reliable_votes": 0,
        "majority_label": predicted_label,
        "majority_verdict": pred_verdict,
        "effective_label": predicted_label,
        "effective_verdict": pred_verdict,
        "verdict_source": "ml_model",
        "feedback_status": "assumed_accurate",
        "individual_feedbacks": []
    }
    return new_record, None


def record_new_query_in_dataset(
    text: str,
    headline: str,
    article: str,
    predicted_label: int,
    confidence: float,
    top_fake_words: List[str],
    top_reliable_words: List[str]
) -> int:
    """
    Records a new query in both SQLite and datasets/user_feedback.json.
    If the normalized key already exists, increments total_queries only (no duplicates).
    """
    init_db()
    norm = normalize_key(text)
    pred_verdict = "Fake / Misleading" if predicted_label == 1 else "Reliable / Credible"

    # 1. Insert into SQLite history
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prediction_history (
                text, headline, article, prediction, confidence,
                effective_verdict, feedback_status, top_fake_words, top_reliable_words
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            text,
            headline,
            article,
            predicted_label,
            float(confidence),
            pred_verdict,
            "Assumed Accurate",
            json.dumps(top_fake_words),
            json.dumps(top_reliable_words)
        ))
        conn.commit()
        query_id = cursor.lastrowid

    # 2. Upsert consolidated record in datasets/user_feedback.json
    dataset = load_user_feedback_dataset()
    record, idx = _find_or_create_consolidated_record(
        dataset, norm, text, headline, article, predicted_label, confidence
    )

    record["total_queries"] = record.get("total_queries", 0) + 1
    record["last_updated"] = datetime.now().isoformat()

    if idx is None:
        dataset.append(record)
    else:
        dataset[idx] = record

    save_user_feedback_dataset(dataset)
    return query_id


def apply_user_feedback_to_dataset(
    text: str,
    user_label: int,
    user_action: str,
    source_note: Optional[str] = None,
    query_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Records a user vote into the consolidated record for this normalized_key.
    Recomputes the majority verdict after each new vote.
    Returns a dict with updated vote counts and effective verdict.
    """
    init_db()
    norm = normalize_key(text)
    user_verdict = "Reliable / Credible" if user_label == 0 else "Fake / Misleading"
    status_label = "User Corrected" if user_action == "disagree" else "User Confirmed"

    # 1. Update consolidated record in datasets/user_feedback.json
    dataset = load_user_feedback_dataset()
    record, idx = _find_or_create_consolidated_record(
        dataset, norm, text, "", "", user_label, 1.0
    )

    # Increment vote count
    if user_label == 1:
        record["fake_votes"] = record.get("fake_votes", 0) + 1
    else:
        record["reliable_votes"] = record.get("reliable_votes", 0) + 1

    # Append individual feedback entry
    record.setdefault("individual_feedbacks", []).append({
        "user_action": user_action,
        "user_label": user_label,
        "source_note": source_note or "",
        "timestamp": datetime.now().isoformat()
    })

    # Recompute majority verdict
    fv = record["fake_votes"]
    rv = record["reliable_votes"]
    model_pred = record.get("model_prediction", 0)

    if fv > rv:
        majority_label = 1
        verdict_source = "majority_user_vote"
    elif rv > fv:
        majority_label = 0
        verdict_source = "majority_user_vote"
    else:
        # Tie — fall back to model prediction
        majority_label = model_pred
        verdict_source = "tie_fallback_ml"

    majority_verdict = "Fake / Misleading" if majority_label == 1 else "Reliable / Credible"

    record["majority_label"] = majority_label
    record["majority_verdict"] = majority_verdict
    record["effective_label"] = majority_label
    record["effective_verdict"] = majority_verdict
    record["verdict_source"] = verdict_source
    record["feedback_status"] = "community_consensus"
    record["last_updated"] = datetime.now().isoformat()

    if idx is None:
        dataset.append(record)
    else:
        dataset[idx] = record

    save_user_feedback_dataset(dataset)

    # 2. Log individual feedback to SQLite feedbacks table
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedbacks (text, predicted_label, confidence, user_label, user_action, feedback_status, source_note, applied_to_model)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            text,
            record.get("model_prediction", 1 - user_label if user_action == "disagree" else user_label),
            1.0,
            user_label,
            user_action,
            status_label,
            source_note or ""
        ))
        conn.commit()

        # Update prediction_history verdict/status for this text
        if norm:
            conn.execute("""
                UPDATE prediction_history
                SET effective_verdict = ?, feedback_status = ?
                WHERE text = ?
            """, (majority_verdict, status_label, text))
            conn.commit()

    return {
        "fake_votes": fv,
        "reliable_votes": rv,
        "total_votes": fv + rv,
        "majority_verdict": majority_verdict,
        "majority_label": majority_label,
        "verdict_source": verdict_source
    }


def get_stats() -> Dict[str, Any]:
    init_db()
    dataset = load_user_feedback_dataset()
    total_stored = len(dataset)
    community_consensus = sum(1 for d in dataset if d.get("verdict_source") == "majority_user_vote")
    tie_fallback = sum(1 for d in dataset if d.get("verdict_source") == "tie_fallback_ml")
    ml_only = sum(1 for d in dataset if d.get("verdict_source") == "ml_model")
    total_fake_votes = sum(d.get("fake_votes", 0) for d in dataset)
    total_reliable_votes = sum(d.get("reliable_votes", 0) for d in dataset)

    return {
        "total_queries_in_dataset": total_stored,
        "community_consensus_count": community_consensus,
        "tie_fallback_count": tie_fallback,
        "ml_model_only_count": ml_only,
        "total_fake_votes_ever": total_fake_votes,
        "total_reliable_votes_ever": total_reliable_votes,
        # Legacy keys kept for backward compatibility
        "user_corrected_count": community_consensus,
        "user_confirmed_count": 0,
        "assumed_accurate_count": ml_only,
        "dataset_file_path": str(USER_FEEDBACK_DATASET_FILE)
    }


def get_recent_history(limit: int = 15) -> List[Dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, text, headline, article, prediction, confidence, effective_verdict, feedback_status, top_fake_words, top_reliable_words, timestamp
            FROM prediction_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["top_fake_words"] = json.loads(d["top_fake_words"]) if d.get("top_fake_words") else []
            d["top_reliable_words"] = json.loads(d["top_reliable_words"]) if d.get("top_reliable_words") else []
            result.append(d)
        return result


def get_recent_feedbacks(limit: int = 15) -> List[Dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, text, predicted_label, confidence, user_label, user_action, feedback_status, source_note, timestamp
            FROM feedbacks
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
    print("User feedback dataset initialized at:", USER_FEEDBACK_DATASET_FILE)
    print("Stats:", get_stats())
