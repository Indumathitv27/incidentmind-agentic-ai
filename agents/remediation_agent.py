from __future__ import annotations
from typing import Any, Dict, List


def build_remediation_plan(
    rca_hypothesis: Dict[str, Any],
    incident_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Remediation Agent (V1): produce safe, ranked remediation steps + validation checks.
    No execution, suggestions only.
    """
    root = (rca_hypothesis.get("root_cause") or "").lower()
    confidence = float(rca_hypothesis.get("confidence") or 0.0)

    steps: List[Dict[str, str]] = []
    validation: List[str] = []
    notes: List[str] = []

    # Common validation checks
    validation.extend([
        "Confirm error_rate returns to baseline",
        "Confirm latency_p95_ms returns to baseline",
        "Confirm no new ERROR patterns appear in logs",
    ])

    # DB pool / DB connectivity remediation
    if "connection pool" in root or "db connectivity" in root or "database" in root:
        steps.extend([
            {"step": "Check DB connection pool utilization and active connections (read-only query/metrics)", "risk": "low"},
            {"step": "Review recent deployments/config changes related to DB pool size, timeouts, retries", "risk": "low"},
            {"step": "Identify top slow queries (query logs / APM) and validate indexes/plan regressions", "risk": "medium"},
            {"step": "Temporarily increase DB pool limit or app-side max connections (if approved)", "risk": "medium"},
            {"step": "If regression confirmed, rollback last deployment for the affected service", "risk": "high"},
        ])
        validation.extend([
            "Confirm db_wait_time_ms normalizes",
            "Confirm queue_depth decreases",
        ])
        notes.append("V1 is read-only: this agent only suggests actions; no commands are executed.")

        return {
        "recommended_steps": steps,
        "validation": validation,
        "notes": notes,
    }

