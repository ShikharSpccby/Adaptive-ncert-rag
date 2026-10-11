import httpx

SYSTEM = (
    "You are a maths tutor for NCERT students. Answer ONLY from the numbered context. "
    "If the context does not contain the answer, say so instead of guessing. "
    "Cite sources like [1]. Show calculation steps clearly -- calculations are verified separately."
)


def build_prompt(question: str, hits: list[dict]) -> str:
    ctx = "\n\n".join(
        f"[{i}] (class {h['meta'].get('class_level')}, ch {h['meta'].get('chapter')}, "
        f"p{h['meta'].get('page')}, {h['meta'].get('block_type')})\n{h['text']}"
        for i, h in enumerate(hits, 1)
    )
    return f"Context:\n{ctx}\n\nQuestion: {question}"


def generate(question: str, hits: list[dict], cfg: dict) -> str:
    prompt = build_prompt(question, hits)
    provider = cfg["provider"]
    if provider == "echo":
        return "[echo provider - no LLM called]\n" + prompt
    if provider == "ollama":
        try:
            r = httpx.post(
                f"{cfg['base_url']}/api/chat",
                json={
                    "model": cfg["model"],
                    "stream": False,
                    "options": {"temperature": cfg["temperature"]},
                    "messages": [
                        {"role": "system", "content": SYSTEM},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=300,
            )
            r.raise_for_status()
        except httpx.ConnectError:
            raise SystemExit(
                f"Could not reach Ollama at {cfg['base_url']}. Start it (ollama serve) and make sure "
                f"`ollama pull {cfg['model']}` has been run, or use --set generation.provider=echo."
            )
        return r.json()["message"]["content"]
    raise ValueError(f"unknown generation provider: {provider!r}")
