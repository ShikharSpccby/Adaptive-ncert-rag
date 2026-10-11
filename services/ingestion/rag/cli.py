"""
Run from services/ingestion:
  python -m rag.cli ingest
  python -m rag.cli query "What is the SAS criterion?"
  python -m rag.cli compare
Add  --set key.path=value  (repeatable) to change any config value without touching code.
"""
import argparse
import json
import sys
from pathlib import Path

from .chunking import make_chunks
from .config import load_config, parse_set_args
from .embeddings import get_embedder
from .evaluate import evaluate
from .extract import extract_pdf, parse_filename
from .generate import generate
from .retrieve import retrieve
from .store import add_chunks, get_collection


def _page_of(chunk_text: str, pages: list[str]) -> int:
    probe = " ".join(chunk_text.split())[:60]
    for i, p in enumerate(pages, 1):
        if probe and probe in " ".join(p.split()):
            return i
    return -1


def ingest(cfg: dict, embedder=None) -> int:
    pdfs = sorted(Path(cfg["data"]["pdf_dir"]).glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs in {cfg['data']['pdf_dir']}. Add some (named like class10_ch06_triangles.pdf).")
    embedder = embedder or get_embedder(cfg["embedding"])
    collection = get_collection(cfg["vector_store"], reset=True)
    total = 0
    for pdf in pdfs:
        pages = extract_pdf(pdf)
        if not any(p.strip() for p in pages):
            print(f"  ! {pdf.name}: no text found (scanned PDF? needs OCR) - skipped")
            continue
        meta = parse_filename(pdf)
        chunks = make_chunks("\n\n".join(pages), cfg["chunking"], meta)
        for c in chunks:
            c.meta["page"] = _page_of(c.text, pages)
        add_chunks(collection, chunks, embedder.embed_documents([c.text for c in chunks]), pdf.stem)
        print(f"  {pdf.name}: {len(chunks)} chunks [{cfg['chunking']['strategy']}]")
        total += len(chunks)
    return total


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rag")
    ap.add_argument("command", choices=["ingest", "query", "compare"])
    ap.add_argument("text", nargs="?", help="the question (for `query`)")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    args = ap.parse_args(argv)
    cfg = load_config(overrides=parse_set_args(args.set))

    if args.command == "ingest":
        print(f"Ingested {ingest(cfg)} chunks.")

    elif args.command == "query":
        if not args.text:
            sys.exit('Usage: python -m rag.cli query "your question"')
        embedder = get_embedder(cfg["embedding"])
        hits = retrieve(args.text, get_collection(cfg["vector_store"]), embedder, cfg["retrieval"])
        for i, h in enumerate(hits, 1):
            print(f"[{i}] score={h['score']} {h['meta']}\n{h['text'][:300]}\n")
        if hits:
            print("--- ANSWER ---\n" + generate(args.text, hits, cfg["generation"]))
        else:
            print("Nothing retrieved above min_score.")

    elif args.command == "compare":
        base = cfg["vector_store"]["collection"]
        embedder = get_embedder(cfg["embedding"])
        rows = []
        for s in cfg["evaluation"]["strategies"]:
            c = load_config(overrides={**parse_set_args(args.set),
                                       "chunking": {**cfg["chunking"], "strategy": s},
                                       "vector_store": {**cfg["vector_store"], "collection": f"{base}_{s}"}})
            n = ingest(c, embedder)
            m = evaluate(c["evaluation"]["questions_file"],
                         get_collection(c["vector_store"]), embedder, c["retrieval"])
            rows.append((s, n, m["hit_at_k"], m["mrr"]))
        print(f"\n{'strategy':<12}{'chunks':>8}{'hit@k':>9}{'mrr':>8}")
        for r in rows:
            print(f"{r[0]:<12}{r[1]:>8}{r[2]:>9}{r[3]:>8}")


if __name__ == "__main__":
    main()
