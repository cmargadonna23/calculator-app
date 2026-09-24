"""Main CustomTkinter application window and event wiring."""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.engine import CalculationError, CalculatorEngine
from core.history import HistoryEntry, HistoryManager
from core.state import CalculatorState
from ui.components import CalculatorButton, CalculatorDisplay, HistoryPanel
from ui.styles import (
    APP_NAME,
    COLORS,
    FONT_FAMILY,
    PADDING,
    WINDOW_DEFAULT_SIZE,
    WINDOW_MIN_SIZE,
)


class CalculatorApp(ctk.CTk):
    """Desktop calculator shell. Business logic remains in ``core`` modules."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = CalculatorEngine()
        self.history = HistoryManager()
        self.state = CalculatorState()
        self.state.subscribe(self._render_state)

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_DEFAULT_SIZE[0]}x{WINDOW_DEFAULT_SIZE[1]}")
        self.minsize(*WINDOW_MIN_SIZE)
        self.configure(fg_color=COLORS["window"])
        self._set_icon_if_available()

        ctk.set_default_color_theme("blue")
        ctk.set_appearance_mode("System")

        self._build_layout()
        self._bind_keyboard()
        self._render_state(self.state)
        self._refresh_history()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=3, uniform="main")
        self.grid_columnconfigure(1, weight=2, uniform="main")
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=PADDING, pady=(16, 8))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text=APP_NAME,
            text_color=COLORS["text"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        self.theme_selector = ctk.CTkSegmentedButton(
            header,
            values=["System", "Light", "Dark"],
            command=self._change_theme,
            selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent_hover"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
        )
        self.theme_selector.set("System")
        self.theme_selector.grid(row=0, column=1, padx=(12, 0))

        calculator = ctk.CTkFrame(self, fg_color="transparent")
        calculator.grid(row=1, column=0, sticky="nsew", padx=(PADDING, 9), pady=(0, PADDING))
        calculator.grid_columnconfigure(tuple(range(5)), weight=1, uniform="buttons")
        calculator.grid_rowconfigure(1, weight=1)

        self.display = CalculatorDisplay(calculator)
        self.display.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(0, 14))

        keypad = ctk.CTkFrame(calculator, fg_color="transparent")
        keypad.grid(row=1, column=0, columnspan=5, sticky="nsew")
        for column in range(5):
            keypad.grid_columnconfigure(column, weight=1, uniform="keypad")
        for row in range(6):
            keypad.grid_rowconfigure(row, weight=1)

        layout = [
            [("C", "clear", "danger"), ("⌫", "backspace", "default"), ("(", "(", "operator"), (")", ")", "operator"), ("÷", "/", "operator")],
            [("sin", "sin(", "operator"), ("cos", "cos(", "operator"), ("tan", "tan(", "operator"), ("√", "sqrt(", "operator"), ("×", "*", "operator")],
            [("7", "7", "default"), ("8", "8", "default"), ("9", "9", "default"), ("xʸ", "^", "operator"), ("−", "-", "operator")],
            [("4", "4", "default"), ("5", "5", "default"), ("6", "6", "default"), ("%", "percent", "operator"), ("+", "+", "operator")],
            [("1", "1", "default"), ("2", "2", "default"), ("3", "3", "default"), ("π", "pi", "operator"), ("=", "evaluate", "accent")],
            [("±", "sign", "default"), ("0", "0", "default"), (".", ".", "default"), ("ln", "ln(", "operator"), ("log", "log(", "operator")],
        ]

        for row_index, row in enumerate(layout):
            for column_index, (label, action, variant) in enumerate(row):
                CalculatorButton(
                    keypad,
                    text=label,
                    command=lambda current=action: self._handle_action(current),
                    variant=variant,
                ).grid(
                    row=row_index,
                    column=column_index,
                    sticky="nsew",
                    padx=5,
                    pady=5,
                )

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=1, column=1, sticky="nsew", padx=(9, PADDING), pady=(0, PADDING))
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=1)

        self.history_panel = HistoryPanel(right, on_select=self._load_history_entry)
        self.history_panel.grid(row=0, column=0, sticky="nsew")

        history_actions = ctk.CTkFrame(right, fg_color="transparent")
        history_actions.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        history_actions.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            history_actions,
            text="Export",
            command=self._export_history,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            history_actions,
            text="Clear History",
            command=self._clear_history,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _handle_action(self, action: str) -> None:
        if action == "clear":
            self.state.clear()
        elif action == "backspace":
            self.state.backspace()
        elif action == "evaluate":
            self._calculate()
        elif action == "percent":
            self.state.apply_percent()
        elif action == "sign":
            self.state.toggle_sign()
        else:
            self.state.append(action)

    def _calculate(self) -> None:
        expression = self.state.expression
        if not expression and self.state.just_evaluated:
            expression = self.state.display
        try:
            value = self.engine.evaluate(expression)
            result = self.engine.format_result(value)
        except CalculationError as exc:
            self.state.set_error(str(exc))
            return

        self.history.add(expression, result)
        self.state.set_result(expression, result)
        self._refresh_history()

    def _render_state(self, state: CalculatorState) -> None:
        expression_context = state.expression if state.just_evaluated else ""
        self.display.update_content(expression_context, state.display, state.status)

    def _refresh_history(self) -> None:
        self.history_panel.render(self.history.entries)

    def _load_history_entry(self, entry: HistoryEntry) -> None:
        self.state.set_expression(entry.expression)

    def _export_history(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export calculation history",
            defaultextension=".csv",
            filetypes=[
                ("CSV file", "*.csv"),
                ("JSON file", "*.json"),
                ("Text file", "*.txt"),
            ],
        )
        if not path:
            return
        try:
            exported = self.history.export(Path(path))
        except (OSError, ValueError) as exc:
            messagebox.showerror("Export failed", str(exc), parent=self)
            return
        messagebox.showinfo("History exported", f"Saved to:\n{exported}", parent=self)

    def _clear_history(self) -> None:
        if not self.history.entries:
            return
        confirmed = messagebox.askyesno(
            "Clear history",
            "Delete all saved calculation history?",
            parent=self,
        )
        if confirmed:
            self.history.clear()
            self._refresh_history()

    def _change_theme(self, mode: str) -> None:
        ctk.set_appearance_mode(mode)

    def _bind_keyboard(self) -> None:
        self.bind("<Return>", lambda _event: self._calculate())
        self.bind("<KP_Enter>", lambda _event: self._calculate())
        self.bind("<Escape>", lambda _event: self.state.clear())
        self.bind("<BackSpace>", lambda _event: self.state.backspace())
        self.bind("<Key>", self._on_key)

    def _on_key(self, event) -> str | None:
        # Ignore keys already handled by dedicated bindings.
        if event.keysym in {"Return", "KP_Enter", "Escape", "BackSpace"}:
            return None

        char = event.char
        if char in "0123456789.+-*/()^":
            self.state.append(char)
            return "break"
        if char == "%":
            self.state.apply_percent()
            return "break"
        return None

    def _set_icon_if_available(self) -> None:
        icon = Path(__file__).resolve().parents[1] / "main.ico"
        if icon.exists():
            try:
                self.iconbitmap(str(icon))
            except Exception:
                # Some Linux/Tk builds do not support .ico via iconbitmap.
                pass


def main() -> None:
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
