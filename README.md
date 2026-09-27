# Adaptive NCERT Math Tutor

AI-powered platform that turns NCERT Math textbooks (Classes 1–12) into personalized video lessons,
adaptive remediation, and diagnostic testing.

**Status:** Stage 0 — repo scaffold only, no functional code yet. See `docs/` for architecture.

## Layout

```
apps/web/                # Next.js frontend (not started)
services/ingestion/       # PDF -> concept graph extraction
services/content-gen/      # LLM script + Manim code generation
services/verify/           # SymPy/CAS verification service — build this first
services/render-worker/    # Sandboxed Manim + FFmpeg rendering
services/tts-align/        # TTS + audio/video timing alignment
services/diagnostic-engine/# Mastery tracking (BKT-style) + remediation routing
services/item-bank/        # Question generation + difficulty tracking
graph/                     # Knowledge graph schema/migrations
infra/                     # Deployment configs (Docker, etc.)
docs/                      # Architecture documents
```

## Setup

1. Copy `.env.example` to `.env` and fill in real values (never commit `.env`).
2. (Coming in later stages: Postgres setup, FastAPI service, Docker.)

## Build order

Following the lean v1 plan: `verify` service first, then `ingestion`, then `content-gen` +
`render-worker` together, then `diagnostic-engine`, then `apps/web`.
