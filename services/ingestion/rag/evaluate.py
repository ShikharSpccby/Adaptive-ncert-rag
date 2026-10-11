import json

from .retrieve import retrieve


def evaluate(questions_file: str, collection, embedder, retrieval_cfg: dict) -> dict:
    """questions_file: [{"question": "...", "expected": "text that must appear in a correct chunk"}]
    hit@k = a retrieved chunk contains `expected`; mrr rewards ranking it higher."""
    with open(questions_file) as f:
        items = json.load(f)
    hits_at_k, rr = 0, 0.0
    for item in items:
        got = retrieve(item["question"], collection, embedder, retrieval_cfg)
        rank = next(
            (i for i, h in enumerate(got, 1) if item["expected"].lower() in h["text"].lower()), None
        )
        if rank:
            hits_at_k += 1
            rr += 1.0 / rank
    n = len(items) or 1
    return {"n": len(items), "hit_at_k": round(hits_at_k / n, 3), "mrr": round(rr / n, 3)}
