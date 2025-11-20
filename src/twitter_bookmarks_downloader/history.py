from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


HistoryData = Dict[str, Dict[str, Any]]


def load_history(path: Path) -> HistoryData:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
        return {}
    except json.JSONDecodeError:
        return {}


def save_history(path: Path, history: HistoryData) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

