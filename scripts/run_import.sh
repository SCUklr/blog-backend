#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Working in $ROOT_DIR"

# check if server is already up
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/docs | grep -q "200"; then
  echo "[INFO] FastAPI already responding at /docs"
else
  echo "[INFO] FastAPI not responding. Will try to start after preparing venv."
fi

# Ensure venv exists and activate it (always do this so import runs inside venv)
if [ ! -d ".venv" ]; then
  echo "[INFO] Creating venv .venv"
  python3 -m venv .venv
else
  echo "[INFO] .venv already exists"
fi

# shellcheck disable=SC1091
source .venv/bin/activate
echo "[INFO] Upgrading pip and ensuring requirements are installed (may be quick if already installed)"
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Start uvicorn if it wasn't responding earlier
if ! curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/docs | grep -q "200"; then
  echo "[INFO] Starting uvicorn in background (logs->uvicorn.log)"
  nohup .venv/bin/python -m uvicorn app.main:app --reload --port 8000 > uvicorn.log 2>&1 &
  sleep 2
else
  echo "[INFO] FastAPI already up; skipping start"
fi

echo "[INFO] Running import script inside venv"
python scripts/import_md.py

EXIT_CODE=$?
if [ "$EXIT_CODE" -eq 0 ]; then
  echo "[INFO] Import script completed successfully"
else
  echo "[WARN] Import script exited with code $EXIT_CODE"
fi

# print last 30 lines of uvicorn.log to help debugging
if [ -f uvicorn.log ]; then
  echo "---- uvicorn.log (tail 30) ----"
  tail -n 30 uvicorn.log
fi

exit $EXIT_CODE
