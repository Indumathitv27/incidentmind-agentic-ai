from __future__ import annotations
from pathlib import Path
from typing import List

LIVE_LOG_DIR = Path(__file__).resolve().parents[1] / "data" / "live_logs"

def fetch_logs(service: str, limit: int = 500) -> List[str]:
    """
    Tool (V1): read the latest log lines for a service from a local live log file.
    Later we can swap this with CloudWatch/Datadog/ELK.
    """
    file_path = LIVE_LOG_DIR / f"{service}.log"
    if not file_path.exists():
        return []

    lines = file_path.read_text(encoding="utf-8").splitlines()
    return lines[-limit:]
