from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

LIVE_METRICS_DIR = Path(__file__).resolve().parents[1] / "data" / "live_metrics"

def fetch_metrics(service: str, limit: int = 120) -> List[Dict[str, Any]]:
    """
    Tool (V1): Read recent metrics events (JSONL) for a service.
    Returns list of dicts: [{"ts":..., "service":..., "metrics": {...}}, ...]
    """
    file_path = LIVE_METRICS_DIR / f"{service}.jsonl"
    if not file_path.exists():
        return []

    lines = file_path.read_text(encoding="utf-8").splitlines()
    lines = lines[-limit:]
    out: List[Dict[str, Any]] = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
