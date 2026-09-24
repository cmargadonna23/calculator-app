"""Visual design tokens for the CustomTkinter interface."""

from __future__ import annotations

APP_NAME = "Calculator Pro"
WINDOW_MIN_SIZE = (900, 610)
WINDOW_DEFAULT_SIZE = (1040, 680)

FONT_FAMILY = "Segoe UI"
FONT_MONO = "Cascadia Mono"

# CustomTkinter accepts (light_mode_color, dark_mode_color) tuples.
COLORS = {
    "window": ("#F4F6F8", "#111318"),
    "surface": ("#FFFFFF", "#1B1F27"),
    "surface_alt": ("#EDF1F5", "#242A34"),
    "border": ("#D9E0E8", "#343C49"),
    "text": ("#15202B", "#F5F7FA"),
    "muted": ("#667085", "#9AA4B2"),
    "accent": ("#4F46E5", "#7C74FF"),
    "accent_hover": ("#4338CA", "#8B84FF"),
    "operator": ("#E8ECFF", "#303856"),
    "operator_hover": ("#DCE2FF", "#3B466C"),
    "danger": ("#FDECEC", "#492A2E"),
    "danger_hover": ("#F8D7DA", "#5A3238"),
    "success": ("#157347", "#7EE2A8"),
}

BUTTON_HEIGHT = 58
BUTTON_CORNER_RADIUS = 16
PANEL_CORNER_RADIUS = 20
PADDING = 18
