"""
FastAPI Server & REST API for InfoShield.
Serves web application, REST endpoints for inference, explainability, feedback,
red-teaming categories, and user_feedback dataset management on localhost.
"""

import json
from pathlib import Path
import sys
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.engine import get_engine
from src.database import (
    get_recent_history,
    get_recent_feedbacks,
    load_user_feedback_dataset,
    USER_FEEDBACK_DATASET_FILE
)

DATASETS_DIR = BASE_DIR / "datasets"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
REDTEAM_FILE = DATASETS_DIR / "redteam_categories.json"

app = FastAPI(
    title="InfoShield API",
    description="Explainable Fake News & Disinformation Detection with Continual Learning",
    version="1.0.0"
)

# Enable CORS for Chrome Extension and multi-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Request Schemas
class PredictRequest(BaseModel):
    headline: Optional[str] = Field(None, description="Article headline or title")
    article: Optional[str] = Field(None, description="Full article text or body paragraph")
    text: Optional[str] = Field(None, description="Backwards compatibility statement text")

class FeedbackRequest(BaseModel):
    headline: Optional[str] = None
    article: Optional[str] = None
    text: Optional[str] = None
    query_id: Optional[int] = None
    user_label: int = Field(..., ge=0, le=1, description="0 = Reliable, 1 = Fake")
    user_action: str = Field("disagree", description="'agree' or 'disagree'")
    source_note: Optional[str] = Field(None, description="Optional proof/source or reasoning note")


@app.get("/")
def serve_index():
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found.")
    return FileResponse(index_file)


@app.post("/api/predict")
def predict_news(payload: PredictRequest):
    """
    Classifies news from headline, article body, or both.
    Checks user_feedback memory dataset first before running model.
    """
    engine = get_engine()
    headline = (payload.headline or "").strip()
    article = (payload.article or payload.text or "").strip()

    if headline and article:
        combined_text = f"{headline}. {article}"
        input_type = "both"
    elif headline:
        combined_text = headline
        input_type = "headline_only"
    elif article:
        combined_text = article
        input_type = "article_only"
    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least a Headline, an Article body, or both."
        )

    if len(combined_text) < 3:
        raise HTTPException(status_code=400, detail="Provided text is too short to evaluate.")

    try:
        result = engine.predict_and_explain(combined_text, headline=headline, article=article)
        result["headline"] = headline
        result["article"] = article
        result["input_type"] = input_type
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@app.post("/api/feedback")
def submit_feedback(payload: FeedbackRequest):
    """
    Submits user feedback, updates datasets/user_feedback.json,
    trains online weights via partial_fit, and persists to disk.
    """
    engine = get_engine()
    headline = (payload.headline or "").strip()
    article = (payload.article or "").strip()

    if payload.text and payload.text.strip():
        text_to_learn = payload.text.strip()
    elif headline and article:
        text_to_learn = f"{headline}. {article}"
    elif headline:
        text_to_learn = headline
    elif article:
        text_to_learn = article
    else:
        raise HTTPException(status_code=400, detail="No text provided for feedback.")

    try:
        result = engine.learn_from_feedback(
            text=text_to_learn,
            user_label=payload.user_label,
            user_action=payload.user_action,
            source_note=payload.source_note,
            query_id=payload.query_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback update failed: {str(e)}")


@app.get("/api/redteam/categories")
def get_redteam_categories():
    """Returns 6 benchmark categories with 18 examples each (108 total examples)."""
    if REDTEAM_FILE.exists():
        with open(REDTEAM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.get("/api/dataset/user_feedback")
def get_user_feedback_data():
    """Returns all records stored in datasets/user_feedback.json."""
    return load_user_feedback_dataset()


@app.get("/api/stats")
def get_metrics():
    """Returns model accuracy, sample counts, vocabulary size, and user feedback stats."""
    engine = get_engine()
    return engine.get_stats()


@app.get("/api/history")
def get_query_history(limit: int = 15):
    """Returns recent prediction logs including user feedback memory status."""
    return get_recent_history(limit=limit)


@app.get("/api/feedbacks")
def get_feedback_logs(limit: int = 15):
    """Returns recent user feedback submissions."""
    return get_recent_feedbacks(limit=limit)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host="0.0.0.0", port=8000, reload=True)
