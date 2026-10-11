from .store import _where


def retrieve(query: str, collection, embedder, cfg: dict) -> list[dict]:
    """Cosine-similarity search. Returns hits sorted best-first, each with text, meta, score."""
    res = collection.query(
        query_embeddings=[embedder.embed_query(query)],
        n_results=cfg["top_k"],
        where=_where(cfg.get("filters") or {}),
    )
    hits = []
    for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        score = 1.0 - dist  # cosine distance -> similarity
        if score >= cfg.get("min_score", 0.0):
            hits.append({"text": text, "meta": meta, "score": round(score, 4)})
    return hits
