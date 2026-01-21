from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import os

REPORT_DIR = Path(os.getenv("INCIDENTMIND_REPORT_DIR", (Path(__file__).resolve().parents[1] / "outputs" / "incident_reports").as_posix()))


try:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
except FileExistsError:
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def new_incident_id() -> str:
    return f"inc_{uuid.uuid4().hex[:8]}"

def save_report(incident_id: str, report: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "incident_id": incident_id,
        "created_at": _now_iso(),
        "report": report,
    }
    path = REPORT_DIR / f"{incident_id}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

def load_report(incident_id: str) -> Optional[Dict[str, Any]]:
    path = REPORT_DIR / f"{incident_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
