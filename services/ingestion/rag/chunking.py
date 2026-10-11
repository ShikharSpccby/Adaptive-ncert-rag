import re
from dataclasses import dataclass, field


@dataclass
class Chunk:
    text: str
    meta: dict = field(default_factory=dict)


# split after . ! ? when followed by whitespace + a capital/digit/bracket (so "2.5 cm" survives)
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\\])")
_BLOCK = re.compile(
    r"^\s*(THEOREM|Theorem|DEFINITION|Definition|EXAMPLE|Example|EXERCISE|Exercise|"
    r"SOLUTION|Solution|ACTIVITY|Activity|REMARK|Remark|PROOF|Proof)\b",
    re.M,
)


def split_sentences(text: str) -> list[str]:
    flat = re.sub(r"\s*\n\s*", " ", re.sub(r"[ \t]+", " ", text))
    return [s.strip() for s in _SENT_SPLIT.split(flat) if s.strip()]


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _window(units: list[str], size: int, overlap: int, joiner: str) -> list[str]:
    step = max(1, size - overlap)
    out = []
    for i in range(0, len(units), step):
        window = units[i : i + size]
        if window:
            out.append(joiner.join(window))
        if i + size >= len(units):
            break
    return out


def chunk_by_structure(text: str, max_chars: int = 1500) -> list[tuple[str, str]]:
    """Split on NCERT block headings (Theorem/Example/Exercise/...). A Solution or
    Proof stays attached to the Example/Theorem it belongs to. Returns (text, block_type)."""
    matches = list(_BLOCK.finditer(text))
    if not matches:
        return [(p, "text") for p in split_paragraphs(text)]

    blocks: list[list[str]] = []
    lead = text[: matches[0].start()].strip()
    if lead:
        blocks.append(["text", lead])
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        kind, body = m.group(1).lower(), text[m.start() : end].strip()
        if kind in ("solution", "proof") and blocks:
            blocks[-1][1] += "\n\n" + body
        else:
            blocks.append([kind, body])

    out: list[tuple[str, str]] = []
    for kind, body in blocks:
        if len(body) <= max_chars:
            out.append((body, kind))
            continue
        header = body.splitlines()[0][:80]
        buf, first = "", True
        for p in split_paragraphs(body):
            if buf and len(buf) + len(p) > max_chars:
                out.append((buf, kind))
                buf, first = f"({header}, continued)\n{p}", False
            else:
                buf = f"{buf}\n\n{p}" if buf else p
        if buf:
            out.append((buf, kind))
    return out


def make_chunks(text: str, cfg: dict, base_meta: dict | None = None) -> list[Chunk]:
    strategy = cfg["strategy"]
    base_meta = base_meta or {}
    if strategy == "sentence":
        pieces = [(t, "text") for t in _window(
            split_sentences(text), cfg["sentences_per_chunk"], cfg["overlap"], " ")]
    elif strategy == "paragraph":
        pieces = [(t, "text") for t in _window(
            split_paragraphs(text), cfg["paragraphs_per_chunk"], cfg["overlap"], "\n\n")]
    elif strategy == "structure":
        pieces = chunk_by_structure(text, cfg["max_chars"])
    else:
        raise ValueError(f"unknown chunking strategy: {strategy!r}")
    return [Chunk(t, {**base_meta, "block_type": kind, "strategy": strategy}) for t, kind in pieces]
