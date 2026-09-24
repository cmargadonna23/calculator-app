"""Calculation history persistence and export services."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock


@dataclass(frozen=True)
class HistoryEntry:
    expression: str
    result: str
    timestamp: str

    @classmethod
    def create(cls, expression: str, result: str) -> "HistoryEntry":
        return cls(
            expression=expression,
            result=result,
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )


class HistoryManager:
    """Stores history in JSON and supports TXT, CSV, and JSON exports."""

    def __init__(self, storage_path: Path | None = None, max_entries: int = 250) -> None:
        self.storage_path = storage_path or (
            Path.home() / ".calculator_app" / "history.json"
        )
        self.max_entries = max_entries
        self._lock = RLock()
        self._entries: list[HistoryEntry] = []
        self._load()

    @property
    def entries(self) -> tuple[HistoryEntry, ...]:
        with self._lock:
            return tuple(self._entries)

    def add(self, expression: str, result: str) -> HistoryEntry:
        entry = HistoryEntry.create(expression, result)
        with self._lock:
            self._entries.insert(0, entry)
            del self._entries[self.max_entries :]
            self._save()
        return entry

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self._save()

    def export(self, destination: Path) -> Path:
        destination = destination.expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        suffix = destination.suffix.lower()

        with self._lock:
            if suffix == ".csv":
                self._export_csv(destination)
            elif suffix == ".json":
                self._export_json(destination)
            elif suffix == ".txt":
                self._export_txt(destination)
            else:
                raise ValueError("History export must use .csv, .json, or .txt.")
        return destination

    def _load(self) -> None:
        with self._lock:
            if not self.storage_path.exists():
                return
            try:
                payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
                self._entries = [
                    HistoryEntry(**item)
                    for item in payload
                    if isinstance(item, dict)
                    and {"expression", "result", "timestamp"}.issubset(item)
                ][: self.max_entries]
            except (OSError, json.JSONDecodeError, TypeError):
                # A corrupted optional history file should never stop the calculator.
                self._entries = []

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.storage_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps([asdict(entry) for entry in self._entries], indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.storage_path)

    def _export_csv(self, destination: Path) -> None:
        with destination.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=["timestamp", "expression", "result"]
            )
            writer.writeheader()
            for entry in reversed(self._entries):
                writer.writerow(asdict(entry))

    def _export_json(self, destination: Path) -> None:
        destination.write_text(
            json.dumps([asdict(entry) for entry in self._entries], indent=2),
            encoding="utf-8",
        )

    def _export_txt(self, destination: Path) -> None:
        lines = [
            f"{entry.timestamp} | {entry.expression} = {entry.result}"
            for entry in reversed(self._entries)
        ]
        destination.write_text("\n".join(lines), encoding="utf-8")
