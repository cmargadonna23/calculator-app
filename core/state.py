"""Application state model independent from the UI toolkit."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

StateListener = Callable[["CalculatorState"], None]


@dataclass
class CalculatorState:
    expression: str = ""
    display: str = "0"
    status: str = "Ready"
    just_evaluated: bool = False
    has_error: bool = False
    _listeners: list[StateListener] = field(default_factory=list, repr=False)

    def subscribe(self, listener: StateListener) -> None:
        self._listeners.append(listener)

    def set_expression(self, expression: str) -> None:
        self.expression = expression
        self.display = expression or "0"
        self.just_evaluated = False
        self.has_error = False
        self.status = "Editing"
        self._notify()

    def append(self, token: str) -> None:
        operators = {"+", "-", "*", "/", "^", "%"}
        function_prefixes = {"sqrt(", "sin(", "cos(", "tan(", "ln(", "log("}

        if self.has_error:
            self.clear(notify=False)

        if self.just_evaluated:
            if token in operators:
                self.expression = self.display + token
            elif token in function_prefixes:
                self.expression = f"{token}{self.display})"
            else:
                self.expression = token
            self.just_evaluated = False
        else:
            self.expression += token

        self.display = self.expression or "0"
        self.status = "Editing"
        self._notify()

    def clear(self, *, notify: bool = True) -> None:
        self.expression = ""
        self.display = "0"
        self.status = "Ready"
        self.just_evaluated = False
        self.has_error = False
        if notify:
            self._notify()

    def backspace(self) -> None:
        if self.just_evaluated or self.has_error:
            self.clear()
            return
        self.expression = self.expression[:-1]
        self.display = self.expression or "0"
        self.status = "Editing" if self.expression else "Ready"
        self._notify()

    def set_result(self, expression: str, result: str) -> None:
        self.expression = expression
        self.display = result
        self.status = "Calculated"
        self.just_evaluated = True
        self.has_error = False
        self._notify()

    def set_error(self, message: str) -> None:
        self.display = message
        self.status = "Error"
        self.just_evaluated = False
        self.has_error = True
        self._notify()

    def toggle_sign(self) -> None:
        if self.has_error:
            self.clear(notify=False)
        if self.just_evaluated:
            self.expression = f"-({self.display})"
            self.just_evaluated = False
        elif self.expression:
            self.expression = f"-({self.expression})"
        else:
            self.expression = "-"
        self.display = self.expression
        self.status = "Editing"
        self._notify()

    def apply_percent(self) -> None:
        if self.has_error:
            self.clear(notify=False)
        source = self.display if self.just_evaluated else self.expression
        if not source:
            return
        self.expression = f"({source})/100"
        self.display = self.expression
        self.just_evaluated = False
        self.status = "Editing"
        self._notify()

    def _notify(self) -> None:
        for listener in tuple(self._listeners):
            listener(self)
