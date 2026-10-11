import hashlib
import math
import re


class FakeEmbedder:
    """Offline stand-in (hashed bag-of-words). Lets you test the whole pipeline without
    downloading a model. Retrieval quality is keyword-level only -- never use it for real results."""

    def __init__(self, dim: int = 256):
        self.dim = dim

    def _vec(self, text: str) -> list[float]:
        v = [0.0] * self.dim
        for tok in re.findall(r"[a-z0-9]+", text.lower()):
            v[int(hashlib.md5(tok.encode()).hexdigest(), 16) % self.dim] += 1.0
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norm for x in v]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vec(text)


class STEmbedder:
    """EmbeddingGemma via sentence-transformers. encode_query / encode_document apply the
    model's own query/document prompts -- don't hand-write prefixes."""

    def __init__(self, model_name: str, batch_size: int = 16):
        from sentence_transformers import SentenceTransformer  # heavy import, keep it lazy

        self.model = SentenceTransformer(model_name)
        self.batch_size = batch_size

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode_document(texts, batch_size=self.batch_size).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode_query(text).tolist()


def get_embedder(cfg: dict):
    provider = cfg["provider"]
    if provider == "fake":
        return FakeEmbedder()
    if provider == "sentence_transformers":
        return STEmbedder(cfg["model"], cfg.get("batch_size", 16))
    raise ValueError(f"unknown embedding provider: {provider!r}")
