#!/usr/bin/env bash
set -euo pipefail
# Stop any process listening on port 8000 (uvicorn default)
PORT=8000
PIDS=$(lsof -ti tcp:${PORT} || true)
if [ -z "$PIDS" ]; then
  echo "No process listening on port $PORT"
  exit 0
fi

echo "Killing processes on port $PORT: $PIDS"
kill $PIDS || true
sleep 1
# verify
PIDS2=$(lsof -ti tcp:${PORT} || true)
if [ -z "$PIDS2" ]; then
  echo "Stopped."
  exit 0
else
  echo "Still running: $PIDS2"
  exit 2
fi
