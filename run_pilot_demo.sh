#!/usr/bin/env bash
# Runs Stage 2 (verify) + Stage 3 (render-worker) together as one integrated pipeline.
#
# What this proves: the render-worker is USELESS without the verify service running --
# it calls it over HTTP and refuses to render if verification fails or is unreachable.
# This script is the "integration" of stages 2 and 3; Stage 1 is just the repo holding both.
#
# Usage: ./run_pilot_demo.sh
# Requires: each service's requirements already installed (see their READMEs),
#           OR run `pip install -r requirements-dev.txt` once at repo root.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFY_DIR="$REPO_ROOT/services/verify"
RENDER_DIR="$REPO_ROOT/services/render-worker"
VERIFY_PORT=8001

cleanup() {
  if [[ -n "${VERIFY_PID:-}" ]]; then
    echo "Shutting down verify service (pid $VERIFY_PID)..."
    kill "$VERIFY_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "== Starting verify service (Stage 2) on port $VERIFY_PORT =="
(cd "$VERIFY_DIR" && uvicorn app.main:app --port "$VERIFY_PORT" > /tmp/verify_service.log 2>&1) &
VERIFY_PID=$!

echo "== Waiting for verify service to be healthy =="
for i in $(seq 1 20); do
  if curl -s "http://localhost:$VERIFY_PORT/health" > /dev/null 2>&1; then
    echo "verify service is up."
    break
  fi
  if [[ "$i" -eq 20 ]]; then
    echo "verify service did not start in time. Check /tmp/verify_service.log"
    exit 1
  fi
  sleep 0.5
done

echo "== Running render pipeline (Stage 3), gated on verification =="
(cd "$RENDER_DIR" && python render_concept.py)

echo ""
echo "== Done. Output video: =="
find "$RENDER_DIR/output" -name "*.mp4" -path "*SolveLinearEquation.mp4" 2>/dev/null || true
