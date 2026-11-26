@echo off
echo ==========================================================
echo  InfoShield: Disinformation Detection & Continual Learning
echo ==========================================================
cd /d "%~dp0"

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo Starting InfoShield server at http://localhost:8000 ...
uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
pause
