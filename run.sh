#!/usr/bin/env bash
# InfoShield Web Application Launcher (Cross-Platform for Linux / macOS)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "🛡️  InfoShield: Disinformation Detection & Continual Learning"
echo "=========================================================="

# Auto-setup virtual environment if not present on this machine
if [ ! -d ".venv" ]; then
    echo "First-time setup detected. Creating virtual environment..."
    python3 -m venv .venv
    echo "Installing required packages from requirements.txt..."
    ./.venv/bin/pip install -r requirements.txt
fi

echo "Starting InfoShield server at http://localhost:8000"
echo "Press Ctrl+C to stop."
echo "=========================================================="

"$SCRIPT_DIR/.venv/bin/uvicorn" src.server:app --host 0.0.0.0 --port 8000 --reload
