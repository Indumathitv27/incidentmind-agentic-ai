from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


ALLOWED_CATEGORIES = {
    "db_connectivity",
    "latency",
    "deployment_issue",
    "auth",
    "dependency_down",
    "unknown",
}


def _detect_symptoms(signals: Dict[str, Any]) -> List[str]:
    symptoms: List[str] = []

    # Heuristics (tune later)
    error_rate = signals.get("error_rate")
    if isinstance(error_rate, (int, float)) and error_rate >= 0.10:
        symptoms.append("error_rate_spike")

    latency_p95 = signals.get("latency_p95_ms")
    if isinstance(latency_p95, (int, float)) and latency_p95 >= 800:
        symptoms.append("latency_spike_p95")

    db_wait = signals.get("db_wait_time_ms")
    if isinstance(db_wait, (int, float)) and db_wait >= 300:
        symptoms.append("db_wait_spike")

    if not symptoms:
        symptoms.append("no_clear_symptoms")

    return symptoms


def _classify_category(symptoms: List[str]) -> str:
    # Simple mapping rules (LLM later)
    if "db_wait_spike" in symptoms:
        return "db_connectivity"
    if "error_rate_spike" in symptoms and "latency_spike_p95" in symptoms:
        return "dependency_down"
    if "latency_spike_p95" in symptoms:
        return "latency"
    if "error_rate_spike" in symptoms:
        return "unknown"
    return "unknown"


def build_incident_context(
    *,
    service: str,
    severity: str,
    time_window_minutes: int,
    signals: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Alert Agent (V1): Rule-based incident context builder.
    Later, we will replace/augment with an LLM-based classifier.
    """
    signals = signals or {}
    symptoms = _detect_symptoms(signals)
    category = _classify_category(symptoms)
    if category not in ALLOWED_CATEGORIES:
        category = "unknown"

    questions: List[str] = []
    if category in {"unknown", "dependency_down"}:
        questions.append("Did any deployments occur in the last 60 minutes?")
    if category in {"db_connectivity"}:
        questions.append("Are DB connection pool metrics available (utilization, timeouts)?")

    return {
        "service": service,
        "severity": severity,
        "time_window_minutes": time_window_minutes,
        "symptoms": symptoms,
        "category": category,
        "questions": questions,
    }
