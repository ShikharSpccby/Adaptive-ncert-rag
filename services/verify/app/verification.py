"""
Math verification core.

WHY THIS FILE IS WRITTEN THE WAY IT IS:
SymPy's own `sympify()` parses strings by calling Python's `eval()` under the hood.
That means a naive `sympify(llm_output_string)` can execute arbitrary Python if the
LLM-generated string contains something like `__import__('os').system(...)` —
this is a real, documented risk with sympify on untrusted input, not a theoretical one.

Everything here goes through `safe_parse()`, which uses `parse_expr()` with an
explicit, stripped-down `global_dict` (no builtins) instead of raw `sympify()`.
This is the SymPy-recommended pattern for untrusted input. Nothing in this service
should ever call bare `sympify()` on a string that came from an LLM.
"""

from __future__ import annotations

from typing import Optional

import sympy
from sympy import Eq, simplify, symbols
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

_SAFE_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)

# parse_expr's transformations rewrite numeric literals into calls like
# Integer(2)/Float(1.5), so the eval'd code needs those names available -- but
# ONLY these names, and explicitly nothing from real Python builtins
# (no __import__, open, exec, eval). This dict is the actual security boundary:
# everything a legitimate math expression needs, nothing a malicious one does.
_ALLOWED_GLOBALS = {
    "Integer": sympy.Integer,
    "Float": sympy.Float,
    "Rational": sympy.Rational,
    "Symbol": sympy.Symbol,
    "pi": sympy.pi,
    "E": sympy.E,
    "I": sympy.I,
    "oo": sympy.oo,
    "sqrt": sympy.sqrt,
    "sin": sympy.sin,
    "cos": sympy.cos,
    "tan": sympy.tan,
    "log": sympy.log,
    "exp": sympy.exp,
    "Abs": sympy.Abs,
    "__builtins__": {},  # strips real Python builtins from the eval namespace
}


def safe_parse(expr_str: str, allowed_symbols: Optional[list[str]] = None):
    """
    Parse an untrusted math expression string into a SymPy expression without
    exposing Python builtins to the parser. Only the symbol names explicitly
    passed in `allowed_symbols`, plus a fixed, curated set of SymPy math names
    (see _ALLOWED_GLOBALS), can resolve to anything in this eval namespace --
    nothing from `__builtins__` is reachable.
    """
    allowed_symbols = allowed_symbols or []
    local_syms = {name: symbols(name) for name in allowed_symbols}
    global_dict = dict(_ALLOWED_GLOBALS)
    return parse_expr(
        expr_str,
        local_dict=local_syms,
        global_dict=global_dict,
        transformations=_SAFE_TRANSFORMATIONS,
    )


def verify_algebraic_equivalence(
    llm_expr: str, reference_expr: str, allowed_symbols: list[str]
) -> bool:
    """
    True if llm_expr and reference_expr are the same expression up to algebraic
    simplification (e.g. "x**2 - 1" vs "(x-1)*(x+1)").
    """
    lhs = safe_parse(llm_expr, allowed_symbols)
    rhs = safe_parse(reference_expr, allowed_symbols)
    return simplify(lhs - rhs) == 0


def verify_equation_roots(
    equation_str: str, symbol_name: str, claimed_roots: list[str]
) -> dict:
    """
    Solves `equation_str` (must contain exactly one '=') for `symbol_name` and
    checks whether `claimed_roots` matches the actual solution set.
    """
    if equation_str.count("=") != 1:
        raise ValueError("equation_str must contain exactly one '='")

    from sympy import solve

    x = symbols(symbol_name)
    lhs_str, rhs_str = equation_str.split("=", 1)
    lhs = safe_parse(lhs_str, [symbol_name])
    rhs = safe_parse(rhs_str, [symbol_name])
    true_roots = solve(Eq(lhs, rhs), x)

    parsed_claims = [safe_parse(r, [symbol_name]) for r in claimed_roots]

    # Compare as sets of simplified values so equivalent-but-differently-written
    # roots (e.g. "2" vs "4/2") still match.
    true_set = {simplify(r) for r in true_roots}
    claimed_set = {simplify(r) for r in parsed_claims}

    return {
        "correct": true_set == claimed_set,
        "true_roots": [str(r) for r in true_roots],
        "claimed_roots": claimed_roots,
    }


def verify_numeric_answer(
    expression_str: str,
    claimed_value: float,
    allowed_symbols: Optional[list[str]] = None,
    tolerance: float = 1e-6,
) -> dict:
    """
    Evaluates `expression_str` numerically and checks it against `claimed_value`
    within `tolerance`. For plain arithmetic checks (e.g. a generated item's
    answer key) rather than symbolic equivalence.
    """
    expr = safe_parse(expression_str, allowed_symbols)
    evaluated = float(expr.evalf())
    return {
        "correct": abs(evaluated - claimed_value) < tolerance,
        "evaluated": evaluated,
    }
