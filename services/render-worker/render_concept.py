"""
This script stands in for what the Planner + verification step of the real
pipeline will do automatically. It explicitly checks every mathematical claim
in the "2x + 3 = 7" lesson against the verify service running on localhost:8001
BEFORE allowing the Manim render to run. If any check fails, the render is
refused -- this is the enforcement point for "nothing unverified becomes a video."
"""

import subprocess
import sys

import httpx

VERIFY_URL = "http://localhost:8001"


def check(label: str, endpoint: str, payload: dict) -> bool:
    try:
        resp = httpx.post(f"{VERIFY_URL}{endpoint}", json=payload, timeout=10)
        resp.raise_for_status()
    except httpx.ConnectError:
        print(
            f"\nCould not reach the verify service at {VERIFY_URL}.\n"
            "The render pipeline refuses to run without it -- that's intentional,\n"
            "not a bug. Start it first: cd services/verify && uvicorn app.main:app --port 8001\n"
            "(or just run ./run_pilot_demo.sh from the repo root, which starts both.)"
        )
        sys.exit(1)
    data = resp.json()
    ok = data.get("equivalent", data.get("correct"))
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}: {data}")
    return bool(ok)


def main():
    results = []

    # Step 1: subtracting 3 from both sides of "2x + 3 = 7"
    results.append(check(
        "LHS after -3 (2x+3-3 == 2x)",
        "/verify/equivalence",
        {"llm_expr": "2*x + 3 - 3", "reference_expr": "2*x", "symbols": ["x"]},
    ))
    results.append(check(
        "RHS after -3 (7-3 == 4)",
        "/verify/numeric",
        {"expression": "7 - 3", "claimed_value": 4.0},
    ))

    # Step 2: dividing both sides by 2
    results.append(check(
        "LHS after /2 ((2x)/2 == x)",
        "/verify/equivalence",
        {"llm_expr": "(2*x)/2", "reference_expr": "x", "symbols": ["x"]},
    ))
    results.append(check(
        "RHS after /2 (4/2 == 2)",
        "/verify/numeric",
        {"expression": "4/2", "claimed_value": 2.0},
    ))

    # Final check: does x=2 actually solve the ORIGINAL equation?
    results.append(check(
        "Final claimed root solves 2x+3=7",
        "/verify/equation-roots",
        {"equation": "2*x + 3 = 7", "symbol": "x", "claimed_roots": ["2"]},
    ))

    if not all(results):
        print("\nOne or more verification checks FAILED. Refusing to render.")
        sys.exit(1)

    print("\nAll math claims verified. Proceeding to render...\n")
    subprocess.run(
        ["manim", "-ql", "scenes/solve_linear_equation.py", "SolveLinearEquation",
         "--media_dir", "output"],
        check=True,
    )


if __name__ == "__main__":
    main()
