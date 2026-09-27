# Math Verification Service

This is the service every other part of the platform depends on: it independently checks
mathematical claims (from an LLM-written script, or a generated question's answer key)
using SymPy, so nothing mathematically wrong ever reaches a rendered video or a student.

## Why `app/verification.py` looks the way it does

SymPy's own `sympify()` parses strings via Python's `eval()`. Fed an untrusted (LLM-generated)
string, that's a real code-execution risk — e.g. `sympify("__import__('os').system('rm -rf /')")`
is not a hypothetical. Every parse in this service goes through `safe_parse()`, which uses
`parse_expr()` with an explicit, curated `global_dict` (only the SymPy names a legitimate math
expression needs — `Integer`, `Symbol`, `sin`, `sqrt`, etc. — and an empty `__builtins__`) instead
of raw `sympify()`. This is the SymPy-recommended pattern for untrusted input.

**Do not add a bare `sympify(some_llm_string)` call anywhere in this service.** If a new function
needs to parse something, route it through `safe_parse()`.

## Run it locally

```bash
cd services/verify
python -m venv .venv && source .venv/bin/activate   # or your preferred env manager
pip install -r requirements.txt

# run the test suite (includes tests that prove malicious input is blocked)
python -m pytest tests/ -v

# start the API
uvicorn app.main:app --reload --port 8001
```

Then, e.g.:

```bash
curl -X POST http://localhost:8001/verify/equivalence \
  -H "Content-Type: application/json" \
  -d '{"llm_expr": "x**2 - 1", "reference_expr": "(x-1)*(x+1)", "symbols": ["x"]}'
# -> {"equivalent": true}
```

## Endpoints

- `GET  /health` — liveness check.
- `POST /verify/equivalence` — are two expressions algebraically the same?
- `POST /verify/equation-roots` — does a claimed set of roots match the actual solution
  of an equation (e.g. checking a generated item's answer key)?
- `POST /verify/numeric` — does an expression evaluate to a claimed numeric value?

## What's deliberately NOT here yet (lean v1 scope)

- WolframAlpha fallback for cases SymPy can't close — add when you hit a real case SymPy fails on,
  not preemptively.
- Caching of repeated verification calls — add once you see real repeated load.
