import chromadb


def get_client(cfg: dict):
    return chromadb.PersistentClient(path=cfg["path"])


def get_collection(cfg: dict, reset: bool = False):
    client = get_client(cfg)
    if reset:
        try:
            client.delete_collection(cfg["collection"])
        except Exception:
            pass
    return client.get_or_create_collection(cfg["collection"], metadata={"hnsw:space": "cosine"})


def add_chunks(collection, chunks, embeddings, id_prefix: str):
    collection.add(
        ids=[f"{id_prefix}-{i}" for i in range(len(chunks))],
        documents=[c.text for c in chunks],
        metadatas=[c.meta for c in chunks],   # Chroma metadata must be str/int/float/bool
        embeddings=embeddings,
    )


def _where(filters: dict):
    if not filters:
        return None
    items = [{k: v} for k, v in filters.items()]
    return items[0] if len(items) == 1 else {"$and": items}
