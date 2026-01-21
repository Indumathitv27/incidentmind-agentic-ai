from __future__ import annotations
from typing import Any, Dict, List


UNSAFE_KEYWORDS = [
    "rm -rf",
    "drop database",
    "delete",
    "format disk",
    "shutdown",
    "exfiltrate",
    "steal",
    "kill -9",
    "wipe",
]


def safety_check(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safety Agent (V1): simple output guardrail.
    - Blocks unsafe remediation language
    - Enforces read-only stance
    """
    notes: List[str] = []
    blocked = False

    # Convert report to a string for a lightweight scan
    blob = str(report).lower()

    for kw in UNSAFE_KEYWORDS:
        if kw in blob:
            blocked = True
            notes.append(f"Blocked unsafe content keyword detected: '{kw}'")

    # Enforce read-only policy reminder
    notes.append("Policy: V1 is read-only; no destructive or automated execution is allowed.")

    return {"blocked": blocked, "notes": notes}
