# RAG Pipeline — Step-by-Step Guide

Goal: chunk NCERT books, embed with EmbeddingGemma, store in a vector DB, retrieve by similarity,
answer with Gemma — with chunking/retrieval fully configurable. Code: `services/ingestion/rag/`.

```
PDF ──extract──▶ text ──chunk──▶ chunks ──embed──▶ vectors ──store──▶ Chroma
                                                                        │
question ──embed──▶ query vector ──similarity search (top_k, filters)───┘
                                         │
                              retrieved chunks ──▶ Gemma ──▶ grounded answer
```

## Step 1 — Prepare your machine
1. Python 3.10+ and a virtual environment (reuse the repo one).
2. `cd services/ingestion && pip install -r requirements.txt`
   (`sentence-transformers` pulls in PyTorch; the first install is large.)
3. Sanity check, no model download needed: `python -m pytest tests/ -v` → 5 tests should pass.

## Step 2 — Get access to the embedding model
EmbeddingGemma (`google/embeddinggemma-300m`) is a **gated** Hugging Face model:
1. Create a Hugging Face account, open the model page, and accept Google's license.
2. Create an access token (Settings → Access Tokens) and run `huggingface-cli login`.
3. Its activations don't support float16 — don't force `model.half()`.

This is not the Gemma chat model: it produces vectors, not text. You need both (Step 3 is the chat one).

## Step 3 — Get a Gemma model for answering
Easiest route is Ollama: install it from ollama.com, then `ollama pull gemma3:4b`
(or whichever Gemma size/tag your lead specified; `ollama list` shows what you have).
Keep `ollama serve` running. No GPU or a weak machine? Pick a smaller model, or test everything else with
`--set generation.provider=echo`, which prints the retrieved context and skips the LLM.

## Step 4 — Put the books in place
Create `services/ingestion/data/pdfs/` and **rename** files to `class<N>_ch<NN>_<name>.pdf`
(e.g. `class10_ch06_triangles.pdf`). NCERT's own names (`jemh106.pdf`) don't say which class/chapter,
and this naming becomes the filterable metadata. Start with 1–2 chapters, not the whole library.
(`data/` is gitignored — PDFs and the vector DB never get committed.)

## Step 5 — Ingest
```bash
cd services/ingestion
python -m rag.cli ingest
```
Prints chunks per file. A "no text found" warning means a scanned PDF (needs OCR — a separate task).
Re-running resets the collection, so change a setting and re-ingest freely.

## Step 6 — Query
```bash
python -m rag.cli query "State the basic proportionality theorem"
```
Shows the top chunks (score + class/chapter/page/block type), then Gemma's answer grounded in them.
**Judge retrieval first**: if the right chunk isn't in the list, the answer can't be good whatever the LLM.

## Step 7 — Change settings without touching code
Everything lives in `rag/config.yaml`; any value can be overridden per run:
```bash
python -m rag.cli ingest --set chunking.strategy=sentence --set chunking.sentences_per_chunk=3
python -m rag.cli query "..." --set retrieval.top_k=8 --set retrieval.min_score=0.35
python -m rag.cli query "..." --set "retrieval.filters={class_level: 10, chapter: 6}"
```
Strategies: `sentence` (N sentences, with overlap), `paragraph` (N paragraphs), `structure`
(one chunk per Theorem / Definition / Example / Exercise, with Solutions and Proofs kept attached).

## Step 8 — Run the actual experiment (what the task asks for)
1. Copy `eval_questions.example.json` → `eval_questions.json`. Write 10–15 questions from your chapter;
   for each, set `expected` to a short string that must appear in the correct chunk (e.g. a theorem number).
2. `python -m rag.cli compare` ingests with every strategy and prints a table:
   chunk count, **hit@k** (was the right chunk retrieved?) and **MRR** (how high was it ranked?).
3. Vary `sentences_per_chunk` (2, 3, 5), `overlap`, and `top_k`, and re-run. That table is your result.

## Step 9 — Known limits (say these in the discussion)
- **Plain-text extraction is lossy.** Formulas and figures come out garbled or missing; inspect a few chunks
  by eye. Upgrade path: Marker or Mathpix for extraction; the chunking/embedding code stays the same.
- **Paragraph chunking depends on blank lines**, which PDF extraction often drops. In my offline test it
  produced a single giant chunk. If you see that, fix extraction or use `sentence` / `structure`.
- **`structure` relies on headings** like "Theorem 6.1" / "EXAMPLE 3" at line starts. Verify on your real books.
- **Gemma's answers aren't math-verified.** Anything numeric still goes through `services/verify` before it can
  reach a student. Small models are weak at multi-step algebra.
- `embedding.provider=fake` is only an offline stand-in for testing the plumbing; never judge quality with it.
- I could not download EmbeddingGemma or run Ollama in my build environment, so those two paths are written
  to their documented APIs but not executed by me. Everything else (chunking, config overrides, Chroma storage,
  filtering, retrieval, the compare table) was run end to end with the stand-in embedder.

## Step 10 — Report back
The table from Step 8, three example queries (one good, one bad), and the limitations above.
Sensible next steps: better extraction, OCR for scanned books, pgvector instead of Chroma, a reranker.
