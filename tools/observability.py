from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict


def new_trace_id() -> str:
    return f"trace_{uuid.uuid4().hex[:12]}"


def log_event(event: str, trace_id: str, payload: Dict[str, Any] | None = None) -> None:
    rec = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": event,
        "trace_id": trace_id,
        "payload": payload or {},
    }
    print(json.dumps(rec, ensure_ascii=False))
