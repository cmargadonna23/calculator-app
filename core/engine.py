"""Safe mathematical expression evaluation for the calculator application."""

from __future__ import annotations

import ast
import math
import operator
import re
from dataclasses import dataclass
from typing import Callable


class CalculationError(ValueError):
    """Raised when an expression cannot be safely or validly evaluated."""


@dataclass(frozen=True)
class EngineConfig:
    """Safety limits for expression evaluation."""

    max_expression_length: int = 250
    max_power_exponent: float = 1_000
    max_factorial_input: int = 170


class CalculatorEngine:
    """
    Evaluate calculator expressions using a restricted Python AST.

    This intentionally avoids ``eval``. Only explicitly allowed operators,
    constants, and math functions can be executed.
    """

    _BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    _UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[float], float]] = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self._functions: dict[str, Callable[..., float]] = {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "ln": math.log,
            "log": math.log10,
            "log10": math.log10,
            "abs": abs,
            "floor": math.floor,
            "ceil": math.ceil,
            "factorial": self._safe_factorial,
        }
        self._constants = {"pi": math.pi, "e": math.e, "tau": math.tau}

    def evaluate(self, expression: str) -> float | int:
        """Normalize, parse, validate, and evaluate an expression."""
        normalized = self.normalize(expression)
        if not normalized:
            raise CalculationError("Enter an expression first.")
        if len(normalized) > self.config.max_expression_length:
            raise CalculationError("Expression is too long.")

        try:
            tree = ast.parse(normalized, mode="eval")
            result = self._evaluate_node(tree.body)
        except CalculationError:
            raise
        except ZeroDivisionError as exc:
            raise CalculationError("Cannot divide by zero.") from exc
        except (SyntaxError, TypeError, ValueError, OverflowError) as exc:
            raise CalculationError("Invalid mathematical expression.") from exc

        if isinstance(result, complex):
            raise CalculationError("Complex-number results are not supported.")
        if isinstance(result, float) and (math.isnan(result) or math.isinf(result)):
            raise CalculationError("Result is outside the supported numeric range.")

        return result

    @staticmethod
    def normalize(expression: str) -> str:
        """Convert calculator glyphs and common user input into parser syntax."""
        value = expression.strip()
        substitutions = {
            "×": "*",
            "÷": "/",
            "−": "-",
            "–": "-",
            "^": "**",
            "π": "pi",
        }
        for source, target in substitutions.items():
            value = value.replace(source, target)

        # Permit a standalone square-root glyph before a number/name/group.
        value = re.sub(r"√\s*(?=\()", "sqrt", value)
        value = re.sub(r"√\s*([A-Za-z0-9_.]+)", r"sqrt(\1)", value)
        return value

    @staticmethod
    def format_result(value: float | int) -> str:
        """Format results compactly while avoiding distracting float artifacts."""
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, int):
            return str(value)
        if value == 0:
            return "0"
        if float(value).is_integer() and abs(value) < 1e15:
            return str(int(value))
        if abs(value) >= 1e12 or abs(value) < 1e-9:
            return f"{value:.10e}".replace("e+", "e")
        return f"{value:.12g}"

    def _evaluate_node(self, node: ast.AST) -> float | int:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise CalculationError("Only numeric values are allowed.")
            return node.value

        if isinstance(node, ast.BinOp):
            operation = self._BINARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise CalculationError("That operator is not supported.")
            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)
            if isinstance(node.op, ast.Pow) and abs(float(right)) > self.config.max_power_exponent:
                raise CalculationError("Exponent is too large.")
            return operation(left, right)

        if isinstance(node, ast.UnaryOp):
            operation = self._UNARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise CalculationError("That unary operator is not supported.")
            return operation(self._evaluate_node(node.operand))

        if isinstance(node, ast.Name):
            if node.id not in self._constants:
                raise CalculationError(f"Unknown constant: {node.id}")
            return self._constants[node.id]

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise CalculationError("Only direct math-function calls are allowed.")
            function = self._functions.get(node.func.id)
            if function is None:
                raise CalculationError(f"Unknown function: {node.func.id}")
            if node.keywords:
                raise CalculationError("Keyword arguments are not supported.")
            arguments = [self._evaluate_node(argument) for argument in node.args]
            try:
                return function(*arguments)
            except TypeError as exc:
                raise CalculationError(f"Invalid arguments for {node.func.id}().") from exc

        raise CalculationError("Expression contains unsupported syntax.")

    def _safe_factorial(self, value: float | int) -> int:
        if isinstance(value, float) and not value.is_integer():
            raise CalculationError("Factorial requires a whole number.")
        integer = int(value)
        if integer < 0:
            raise CalculationError("Factorial requires a non-negative number.")
        if integer > self.config.max_factorial_input:
            raise CalculationError("Factorial input is too large.")
        return math.factorial(integer)
