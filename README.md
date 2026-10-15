# Adaptive NCERT Math Tutor

A project to turn the NCERT maths textbooks (Classes 1-12) into video lessons and practice that
adapt to each student. It is early. Three pieces work on their own, and most of the planned
folders are still empty.

## What works today

**Math verification** (`services/verify`)
A small FastAPI service that checks maths with SymPy: are two expressions equal, are these the
roots of this equation, does this expression evaluate to this number. It parses input with a
restricted parser instead of `sympify`, because `sympify` runs the string as Python and the text
will eventually come from an LLM. Tests are in `services/verify/tests`.


**Textbook search (RAG)** (`services/ingestion`)
Reads NCERT PDFs, splits them into chunks, embeds them with EmbeddingGemma, stores them in
ChromaDB, finds the closest chunks to a question, and has Gemma answer from those chunks (through
Ollama). Chunking can be switched in `rag/config.yaml`:

- `sentence`: split at sentence-ending punctuation, N sentences per chunk
- `paragraph`: split at blank lines, N paragraphs per chunk
- `structure`: split at lines starting with Theorem, Definition, Example, Exercise and so on

`python -m rag.cli compare` scores the three on your own test questions. Steps are in
`docs/rag-step-by-step.md`. It is written directly on PyMuPDF, sentence-transformers and ChromaDB,
without LangChain.

## Not done yet

- The three pieces above are not connected. The RAG output doesn't feed the render pipeline.
- No LLM-written lessons or Manim code, and no narration/TTS.
- No student-facing app, mastery tracking or question bank. The folders exist but are empty.
- PDF text extraction loses formulas and figures, and scanned PDFs need OCR.

## Running it

You need Python 3.10+, ffmpeg, and the Pango/Cairo libraries that Manim uses.

```bash
pip install -r requirements-dev.txt   # verify service + render demo
./run_pilot_demo.sh
```

For the RAG part, see `services/ingestion/README.md`. It has its own requirements file.

## Folders

```
services/verify/             working
services/render-worker/      working (one demo scene)
services/ingestion/          working (RAG experiments)
services/content-gen/        empty
services/tts-align/          empty
services/diagnostic-engine/  empty
services/item-bank/          empty
apps/web/                    empty
graph/  infra/               empty
docs/                        notes and guides
```
