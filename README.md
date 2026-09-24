# Calculator Pro

A modern desktop calculator built with Python and CustomTkinter using a modular, testable architecture.

## Features

- Modern responsive desktop UI with System, Light, and Dark appearance modes
- Standard and scientific operations
- Safe AST-based expression parser; no raw `eval()`
- Parentheses, powers, square root, trigonometry, natural logarithm, base-10 logarithm, π, and e
- Keyboard input and shortcuts
- Persistent calculation history
- History export to CSV, JSON, or TXT
- Independent state-management layer
- Pytest unit tests for calculation logic and error cases

## Architecture

```text
calculator_app/
├── main.ico
├── requirements.txt
├── README.md
├── core/
│   ├── __init__.py
│   ├── engine.py
│   ├── history.py
│   └── state.py
├── ui/
│   ├── __init__.py
│   ├── app.py
│   ├── components.py
│   └── styles.py
└── tests/
    ├── __init__.py
    └── test_engine.py
```

### Responsibilities

- `core/engine.py` — expression normalization, validation, parsing, evaluation, and result formatting.
- `core/history.py` — persistent calculation history plus CSV/JSON/TXT export.
- `core/state.py` — UI-independent application state and observer notifications.
- `ui/components.py` — reusable display, button, and history components.
- `ui/styles.py` — application-wide design tokens and palettes.
- `ui/app.py` — window composition, event binding, keyboard shortcuts, and orchestration.
- `tests/test_engine.py` — unit tests for math behavior and security/error cases.

## Requirements

- Python 3.10+
- Windows, macOS, or Linux with Tk support

## Installation

From the `calculator_app` directory:

```bash
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

Run this command from the project root:

```bash
python -m ui.app
```

## Tests

```bash
pytest -q
```

## Keyboard Shortcuts

| Action | Shortcut |
|---|---|
| Calculate | `Enter` |
| Clear | `Esc` |
| Delete previous character | `Backspace` |
| Operators | `+ - * / ^` |
| Percent | `%` |

## Supported Expression Examples

```text
2 + 3 * 4
(18 / 3) ^ 2
sqrt(144)
sin(pi / 2)
ln(e)
log(1000)
```

Trigonometric functions use **radians**.

## History Storage

History is persisted automatically at:

```text
~/.calculator_app/history.json
```

The application keeps the newest 250 calculations by default.

## Window Icon

`main.ico` is optional. A valid icon is included in this project build. To brand the application, replace it with your own `.ico` file while keeping the same filename. The UI gracefully continues if the current platform cannot use `.ico` through Tk.

## Security Notes

The expression engine does not use Python's unrestricted `eval()`. It parses expressions with `ast.parse()` and recursively evaluates only an explicit allowlist of numeric literals, supported operators, named mathematical constants, and approved mathematical functions.

## Extending the Calculator

To add a new mathematical function:

1. Add the function to `CalculatorEngine._functions` in `core/engine.py`.
2. Add a corresponding UI button or keyboard mapping in `ui/app.py`.
3. Add tests in `tests/test_engine.py`.

This separation keeps UI concerns from leaking into the mathematical domain layer.
