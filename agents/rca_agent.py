from __future__ import annotations
from typing import Any, Dict, List


def _has_error(log_findings: Dict[str, Any], keyword: str) -> bool:
    for item in log_findings.get("top_errors", []):
        if keyword.lower() in str(item.get("pattern", "")).lower():
            return True
    return False


def build_rca_hypothesis(
    incident_context: Dict[str, Any],
    log_findings: Dict[str, Any],
    metric_findings: Dict[str, Any],
) -> Dict[str, Any]:
    """
    RCA Agent (V1): rule-based synthesis of logs + metrics into a hypothesis.
    Later we will upgrade this to LLM-based reasoning with tool safety.
    """
    evidence: List[str] = []
    alternatives: List[str] = []
    confidence = 0.40
    root_cause = "Insufficient evidence (V1)"

    # Signals from logs
    pool_exhausted = _has_error(log_findings, "connection pool exhausted")
    db_timeout = _has_error(log_findings, "DB connection timed out")
    http_500 = _has_error(log_findings, "HTTP 500")

    # Signals from metrics
    anomalies = {a.get("metric") for a in metric_findings.get("anomalies", [])}
    corr = metric_findings.get("correlations", [])

    if pool_exhausted or db_timeout:
        root_cause = "Database connection pool exhaustion / DB connectivity degradation"
        confidence = 0.75
        if pool_exhausted:
            evidence.append("Logs show 'connection pool exhausted'")
        if db_timeout:
            evidence.append("Logs show repeated DB connection timeouts")
        if "db_wait_time_ms" in anomalies:
            confidence += 0.05
            evidence.append("Metric anomaly: db_wait_time_ms threshold breach")
        alternatives.extend(["Network connectivity issues", "Slow queries causing pool saturation"])

    elif "latency_p95_ms" in anomalies and "cpu_pct" in anomalies:
        root_cause = "CPU saturation leading to elevated latency (possible resource contention)"
        confidence = 0.70
        evidence.append("Metric anomaly: latency_p95_ms threshold breach")
        evidence.append("Metric anomaly: cpu_pct threshold breach")
        if "latency spike aligns with high CPU" in corr:
            confidence += 0.05
            evidence.append("Correlation: latency spike aligns with high CPU")
        if http_500:
            evidence.append("Logs show HTTP 500 errors during the window")
        alternatives.extend(["Downstream dependency slowness", "Inefficient code path introduced by deployment"])

    elif http_500:
        root_cause = "Application errors causing HTTP 500 responses"
        confidence = 0.55
        evidence.append("Logs show frequent HTTP 500 Internal Server Error")
        alternatives.extend(["Dependency outage", "Database issues"])

    else:
        # fallback
        confidence = 0.35
        evidence.append("No strong log or metric signature detected")
        alternatives.extend(["Database issue", "Dependency issue", "Deployment regression"])

    # clamp confidence to [0,1]
    confidence = max(0.0, min(1.0, confidence))

    return {
        "root_cause": root_cause,
        "confidence": round(confidence, 2),
        "evidence": evidence,
        "alternatives": alternatives,
    }
