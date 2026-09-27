import pytest

from app.verification import (
    verify_algebraic_equivalence,
    verify_equation_roots,
    verify_numeric_answer,
)


def test_equivalence_true():
    assert verify_algebraic_equivalence("x**2 - 1", "(x-1)*(x+1)", ["x"]) is True


def test_equivalence_false():
    assert verify_algebraic_equivalence("x**2 - 1", "(x-1)*(x+2)", ["x"]) is False


def test_equation_roots_correct():
    result = verify_equation_roots("x**2 - 5*x + 6 = 0", "x", ["2", "3"])
    assert result["correct"] is True


def test_equation_roots_wrong_claim():
    result = verify_equation_roots("x**2 - 5*x + 6 = 0", "x", ["2", "4"])
    assert result["correct"] is False


def test_equation_roots_equivalent_but_different_form():
    # "4/2" should still match "2" -- proves we compare simplified values, not strings
    result = verify_equation_roots("x**2 - 5*x + 6 = 0", "x", ["4/2", "3"])
    assert result["correct"] is True


def test_numeric_correct():
    result = verify_numeric_answer("2 + 2", 4.0)
    assert result["correct"] is True


def test_numeric_incorrect():
    result = verify_numeric_answer("2 + 2", 5.0)
    assert result["correct"] is False


def test_malicious_input_is_blocked_not_executed():
    """
    This is the test that matters most: proves an LLM-authored string that
    attempts a Python builtin call fails to parse instead of executing.
    If this test ever fails, do not ship this service.
    """
    with pytest.raises(Exception):
        verify_algebraic_equivalence("__import__('os').system('echo pwned')", "0", [])


def test_malicious_input_variant_blocked():
    with pytest.raises(Exception):
        verify_numeric_answer("open('/etc/passwd').read()", 0.0)
