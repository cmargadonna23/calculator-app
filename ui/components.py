"""Reusable CustomTkinter UI components."""

from __future__ import annotations

from collections.abc import Callable, Iterable

import customtkinter as ctk

from core.history import HistoryEntry
from ui.styles import (
    BUTTON_CORNER_RADIUS,
    BUTTON_HEIGHT,
    COLORS,
    FONT_FAMILY,
    FONT_MONO,
    PANEL_CORNER_RADIUS,
)


class CalculatorButton(ctk.CTkButton):
    """Consistent calculator button with semantic styling variants."""

    def __init__(
        self,
        master,
        *,
        text: str,
        command: Callable[[], None],
        variant: str = "default",
        **kwargs,
    ) -> None:
        palette = {
            "default": (COLORS["surface_alt"], COLORS["border"], COLORS["text"]),
            "operator": (COLORS["operator"], COLORS["operator_hover"], COLORS["text"]),
            "accent": (COLORS["accent"], COLORS["accent_hover"], "#FFFFFF"),
            "danger": (COLORS["danger"], COLORS["danger_hover"], COLORS["text"]),
        }
        fg, hover, text_color = palette.get(variant, palette["default"])
        super().__init__(
            master,
            text=text,
            command=command,
            height=BUTTON_HEIGHT,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=fg,
            hover_color=hover,
            text_color=text_color,
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            **kwargs,
        )


class CalculatorDisplay(ctk.CTkFrame):
    """Two-level display showing expression context and the active result/value."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=PANEL_CORNER_RADIUS,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)

        self.expression_label = ctk.CTkLabel(
            self,
            text="",
            anchor="e",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(family=FONT_MONO, size=15),
        )
        self.expression_label.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 2))

        self.value_label = ctk.CTkLabel(
            self,
            text="0",
            anchor="e",
            text_color=COLORS["text"],
            font=ctk.CTkFont(family=FONT_MONO, size=38, weight="bold"),
        )
        self.value_label.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="e",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        )
        self.status_label.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 14))

    def update_content(self, expression: str, display: str, status: str) -> None:
        self.expression_label.configure(text=expression if expression != display else "")
        self.value_label.configure(text=display)
        self.status_label.configure(text=status)


class HistoryPanel(ctk.CTkFrame):
    """Scrollable history view with reusable selection callbacks."""

    def __init__(
        self,
        master,
        *,
        on_select: Callable[[HistoryEntry], None],
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=PANEL_CORNER_RADIUS,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self.on_select = on_select
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkLabel(
            self,
            text="History",
            anchor="w",
            text_color=COLORS["text"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=19, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 10))
        self.scroll.grid_columnconfigure(0, weight=1)

    def render(self, entries: Iterable[HistoryEntry]) -> None:
        for child in self.scroll.winfo_children():
            child.destroy()

        entries = list(entries)
        if not entries:
            ctk.CTkLabel(
                self.scroll,
                text="No calculations yet.\nYour recent results will appear here.",
                justify="left",
                anchor="w",
                text_color=COLORS["muted"],
                font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            ).grid(row=0, column=0, sticky="ew", padx=10, pady=12)
            return

        for row, entry in enumerate(entries):
            button = ctk.CTkButton(
                self.scroll,
                text=f"{entry.expression}\n= {entry.result}",
                command=lambda item=entry: self.on_select(item),
                anchor="w",
                fg_color="transparent",
                hover_color=COLORS["surface_alt"],
                text_color=COLORS["text"],
                border_width=0,
                corner_radius=12,
                height=58,
                font=ctk.CTkFont(family=FONT_MONO, size=13),
            )
            button.grid(row=row, column=0, sticky="ew", padx=4, pady=3)
