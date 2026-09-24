"""Unit tests for calculator expression evaluation."""

import math

import pytest

from core.engine import CalculationError, CalculatorEngine, EngineConfig


@pytest.fixture()
def engine() -> CalculatorEngine:
    return CalculatorEngine()


def test_basic_precedence(engine: CalculatorEngine) -> None:
    assert engine.evaluate("2 + 3 * 4") == 14


def test_parentheses(engine: CalculatorEngine) -> None:
    assert engine.evaluate("(2 + 3) * 4") == 20


def test_calculator_glyph_normalization(engine: CalculatorEngine) -> None:
    assert engine.evaluate("8 ÷ 2 × 3") == 12


def test_power_operator(engine: CalculatorEngine) -> None:
    assert engine.evaluate("2 ^ 8") == 256


def test_constants(engine: CalculatorEngine) -> None:
    assert engine.evaluate("pi") == pytest.approx(math.pi)
    assert engine.evaluate("e") == pytest.approx(math.e)


def test_square_root(engine: CalculatorEngine) -> None:
    assert engine.evaluate("sqrt(81)") == 9


def test_trigonometry_uses_radians(engine: CalculatorEngine) -> None:
    assert engine.evaluate("sin(pi / 2)") == pytest.approx(1.0)


def test_logs(engine: CalculatorEngine) -> None:
    assert engine.evaluate("log(1000)") == pytest.approx(3.0)
    assert engine.evaluate("ln(e)") == pytest.approx(1.0)


def test_factorial(engine: CalculatorEngine) -> None:
    assert engine.evaluate("factorial(6)") == 720


def test_division_by_zero_is_friendly_error(engine: CalculatorEngine) -> None:
    with pytest.raises(CalculationError, match="divide by zero"):
        engine.evaluate("10 / 0")


def test_unknown_function_is_rejected(engine: CalculatorEngine) -> None:
    with pytest.raises(CalculationError, match="Unknown function"):
        engine.evaluate("open(1)")


def test_attribute_access_is_rejected(engine: CalculatorEngine) -> None:
    with pytest.raises(CalculationError):
        engine.evaluate("math.sqrt(4)")


def test_non_numeric_literals_are_rejected(engine: CalculatorEngine) -> None:
    with pytest.raises(CalculationError):
        engine.evaluate("'hello'")


def test_oversized_exponent_is_rejected() -> None:
    engine = CalculatorEngine(EngineConfig(max_power_exponent=20))
    with pytest.raises(CalculationError, match="Exponent is too large"):
        engine.evaluate("2 ^ 21")


def test_result_formatting(engine: CalculatorEngine) -> None:
    assert engine.format_result(12.0) == "12"
    assert engine.format_result(1 / 3).startswith("0.333333")
