# 🛡️ InfoShield — AI-Powered Fake News Detection System

> **INT395 Supervised Learning Course Project | Problem Statement #18 — LLM Disinformation Red-Teaming**

InfoShield is a full-stack explainable AI web application that detects disinformation in news headlines and articles. It uses a TF-IDF + SGDClassifier machine learning pipeline trained on 31,421 real-world news samples, with XAI token-attribution explanations, continual online learning, and a majority-vote community feedback system.

---

## 📊 Model Performance

| Metric | Score |
|---|---|
| **Test Accuracy** | **81.3%** |
| **Fake News F1 Score** | **0.8427** |
| **Fake Precision** | **91.5%** |
| **Training Samples** | 31,421 (LIAR + PolitiFact) |
| **Vocabulary Size** | 30,000 TF-IDF features |
| **Model Type** | SGDClassifier (online learning) |

---

## ✨ Features

### 🔍 Dual-Input News Scanner
- Enter a **headline**, **article body**, or **both** — the model adapts its prediction to whatever is provided
- Real-time character counter and input mode indicator
- Quick-load sample presets (Conspiracy, Official, Weather, Space, Politics)
- Synchronized split-stage UI: input shifts left, results slide in from the right

### 📊 Explainable AI (XAI) Results Panel
- **Interactive emoji verdict**: 👍 Green Thumbs Up for Reliable, 👎 Red Thumbs Down for Fake
- Confidence percentage and risk level (High / Moderate / Low / Borderline)
- **Token attribution visualizer**: color-coded word pills showing which words pushed the model toward Fake (red ▲) or Reliable (green ▼) with exact impact scores
- Plain-English rationale explaining the model's reasoning

### 🗳️ Community Majority-Vote Feedback
- After any prediction, submit your feedback (Agree / Correct to Reliable / Correct to Fake)
- Each unique news entry stores **separate Fake and Reliable vote counts**
- When the same news is queried again, InfoShield returns the **majority community verdict** with:
  - 🟥 Fake vote bar / 🟩 Reliable vote bar (percentage fill)
  - `👥 Majority Vote (X Fake vs Y Reliable)` badge
  - If votes are tied, model falls back to ML prediction with `⚖️ Community Tie` notice
- All votes persist in `datasets/user_feedback.json` on the localhost server

### 🧪 Red-Teaming Arena
- **6 benchmark categories** in a 2×3 grid:
  - 🏥 Health & Medical Misinformation
  - 🏛️ Political Disinformation
  - 🌿 Environmental & Climate Denial
  - 🔬 Science & Technology Myths
  - 💰 Financial & Economic Fraud
  - 👥 Social & Cultural Manipulation
- Each category has **18 curated examples** (both Fake and Reliable) with ground-truth labels
- Filter by Fake / Reliable, click **"Test in Scanner ➔"** to run any example instantly

### 📁 Dataset & Transparency Tab
- Live model statistics: accuracy, F1, training samples, vocabulary size
- Full view of `datasets/user_feedback.json` with vote counts, verdict source, and timestamps
- Recent query history from SQLite database
- Community vote totals across all stored entries

### 🌙 Dark / Light Mode
- Defaults to a clean **light theme**
- One-click dark mode toggle in the left sidebar footer
- Preference is remembered in `localStorage`

### 📱 Auto-Collapsible Sidebar
- Sidebar collapses to **72px** (icons only) when not hovered
- Expands to **260px** with full labels on hover
- Main content area is fully responsive — shifts and resizes with the sidebar

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** (Python 3.12 recommended)
- **Git** (to clone the repo)
- No GPU required — runs fully on CPU

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/infoshield.git
cd infoshield
```

### 2. Run the App

**Linux / macOS:**
```bash
chmod +x run.sh
./run.sh
```

**Windows:**
```bat
run.bat
```

The launcher script will:
1. Automatically create a Python virtual environment (`.venv/`)
2. Install all required packages from `requirements.txt`
3. Start the FastAPI server on `http://localhost:8000`

### 3. Open in Browser
Navigate to: **http://localhost:8000**

> **Note:** The pre-trained model (`models/infoshield_active.joblib`) is included. No retraining is needed on a new machine — the model's learned weights are already saved.

### Manual Start (after first run)
```bash
.venv/bin/uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🗂️ Project Structure

```
int395/
├── src/
│   ├── server.py          # FastAPI backend (REST API)
│   ├── engine.py          # ML inference + continual learning engine
│   ├── database.py        # SQLite + user_feedback.json storage
│   ├── model_trainer.py   # TF-IDF + SGDClassifier training pipeline
│   ├── explainer.py       # XAI token attribution engine
│   └── dataset.py         # LIAR + PolitiFact dataset loader
├── templates/
│   └── index.html         # Single-page web application
├── static/
│   ├── css/style.css      # Full UI styling (light/dark themes)
│   └── js/app.js          # Client-side logic
├── datasets/
│   ├── train.tsv          # LIAR dataset — training split (10,240 samples)
│   ├── valid.tsv          # Validation split (1,284 samples)
│   ├── test.tsv           # Test split (1,283 samples)
│   ├── politifact_factcheck_data.json  # PolitiFact dataset (21,152 records)
│   ├── redteam_categories.json         # 6 categories × 18 benchmark examples
│   └── user_feedback.json             # Community feedback memory dataset
├── models/
│   ├── infoshield_active.joblib        # Trained model (1.4 MB, persisted)
│   └── registry.json                  # Model metadata and metrics
├── storage/
│   └── feedback.db        # SQLite: prediction history + individual feedback logs
├── chrome_extension/      # Manifest V3 Chrome Extension
│   ├── manifest.json
│   ├── background.js
│   ├── content.js
│   ├── content.css
│   ├── popup.html
│   └── popup.js
├── run.sh                 # Linux/macOS auto-setup launcher
├── run.bat                # Windows auto-setup launcher
├── requirements.txt       # Python dependencies
└── PROJECT_REQUIREMENTS.md
```

---

## 🔌 Chrome Extension

The InfoShield Chrome Extension lets you detect fake news **directly inside any webpage** — select any text in an article and get an instant verdict from InfoShield.

### Installation Steps

1. **Ensure the InfoShield server is running** at `http://localhost:8000`

2. **Open Chrome** and go to: `chrome://extensions/`

3. **Enable Developer Mode** — toggle it on in the top-right corner

4. **Click "Load unpacked"** and select the `chrome_extension/` folder inside the InfoShield project directory

5. The InfoShield icon will appear in your Chrome toolbar

### How to Use the Extension

**Method 1 — Right-click any selected text:**
1. Go to any news article or webpage
2. **Select / highlight** any sentence, paragraph, or headline
3. Right-click → choose **"Check with InfoShield"** from the context menu
4. A small overlay panel will appear on the page showing the verdict (Fake / Reliable), confidence score, and risk level

**Method 2 — Click the Extension Popup:**
1. Click the InfoShield icon in the Chrome toolbar
2. Paste or type any headline / article text into the popup
3. Click **"Analyze"** to get the verdict

> **Important:** The extension communicates with your local InfoShield server at `http://localhost:8000`. The server must be running for the extension to work. No data is sent to any external server — all analysis is done locally on your machine.

---

## 🧠 How It Works

### Training Pipeline
1. **Data Loading:** LIAR dataset (TSV) + PolitiFact (JSONL) are loaded and normalized to binary labels — `0 = Reliable`, `1 = Fake / Misleading`
2. **Feature Extraction:** TF-IDF vectorizer (30,000 features, unigrams + bigrams, sublinear TF scaling)
3. **Classifier:** SGDClassifier with log loss (logistic regression via SGD) — chosen for its support of `partial_fit()` for online incremental learning
4. **Training:** Trained on 31,421 samples with balanced class weights; achieves 81.3% test accuracy

### Inference Flow
```
User Input (Headline + Article)
        ↓
1. Normalize text
        ↓
2. Check user_feedback.json for community memory
   ├── Community majority votes exist? → Return majority verdict + vote bar
   ├── Votes tied? → Fall back to ML + show tie notice
   └── No votes? → Continue to ML inference
        ↓
3. TF-IDF vectorize
        ↓
4. SGDClassifier.predict_proba()
        ↓
5. XAI token attribution (feature weights × TF-IDF scores)
        ↓
6. Return: verdict, confidence, risk level, rationale, token pills
        ↓
7. Log to SQLite + user_feedback.json
```

### Community Feedback & Continual Learning
- Each user feedback vote is stored in `datasets/user_feedback.json`
- **Majority voting**: If 3 users say Fake and 1 says Reliable → verdict = Fake
- **Tie-breaking**: Equal votes → fall back to ML model prediction
- **Online learning**: Each feedback triggers `classifier.partial_fit()`, updating model weights immediately
- **Model persistence**: Updated weights are saved back to `models/infoshield_active.joblib` after every feedback

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/predict` | Analyze news text — returns verdict, confidence, XAI explanation |
| `POST` | `/api/feedback` | Submit user vote — updates community record and trains model |
| `GET` | `/api/stats` | Model metrics + dataset statistics |
| `GET` | `/api/history?limit=15` | Recent prediction history from SQLite |
| `GET` | `/api/feedbacks?limit=15` | Recent individual feedback logs |
| `GET` | `/api/redteam/categories` | 6 benchmark categories with 18 examples each |
| `GET` | `/api/dataset/user_feedback` | Full contents of `user_feedback.json` |

### Example API Usage
```bash
# Analyze a news headline
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"headline": "Big Pharma Conceals Cancer Cure", "article": ""}'

# Submit community feedback
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"headline": "Big Pharma Conceals Cancer Cure", "user_label": 1, "user_action": "agree"}'
```

---

## 📦 Dependencies

```
fastapi>=0.110.0
uvicorn>=0.28.0
scikit-learn>=1.4.0
pandas>=2.2.0
numpy>=1.26.0
joblib>=1.3.0
python-multipart>=0.0.9
pydantic>=2.6.0
```

---

## 📝 License

This project was developed as a course project for **INT395 — Supervised Learning** at [Your University Name].

---

## ⭐ GitHub

If you found this project useful, please consider starring the repository!

```
https://github.com/YOUR_USERNAME/infoshield
```
