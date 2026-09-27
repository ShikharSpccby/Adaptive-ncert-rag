"""
FastAPI wrapper around app.verification. Run locally with:

    uvicorn app.main:app --reload --port 8001

Then, e.g.:

    curl -X POST http://localhost:8001/verify/equivalence \
      -H "Content-Type: application/json" \
      -d '{"llm_expr": "x**2 - 1", "reference_expr": "(x-1)*(x+1)", "symbols": ["x"]}'
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.verification import (
    verify_algebraic_equivalence,
    verify_equation_roots,
    verify_numeric_answer,
)

app = FastAPI(title="NCERT Tutor — Math Verification Service")


class EquivalenceRequest(BaseModel):
    llm_expr: str
    reference_expr: str
    symbols: list[str]


class EquationRootsRequest(BaseModel):
    equation: str
    symbol: str
    claimed_roots: list[str]


class NumericRequest(BaseModel):
    expression: str
    claimed_value: float
    symbols: list[str] | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/verify/equivalence")
def equivalence(req: EquivalenceRequest):
    try:
        result = verify_algebraic_equivalence(req.llm_expr, req.reference_expr, req.symbols)
    except Exception as e:
        # Parsing failures (malformed or malicious input) come back as a 400,
        # never as a 500 with a stack trace that might leak internals.
        raise HTTPException(status_code=400, detail=f"Could not parse expression: {e}")
    return {"equivalent": result}


@app.post("/verify/equation-roots")
def equation_roots(req: EquationRootsRequest):
    try:
        return verify_equation_roots(req.equation, req.symbol, req.claimed_roots)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not verify equation: {e}")


@app.post("/verify/numeric")
def numeric(req: NumericRequest):
    try:
        return verify_numeric_answer(req.expression, req.claimed_value, req.symbols)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not evaluate expression: {e}")
