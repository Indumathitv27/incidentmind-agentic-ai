from __future__ import annotations
from typing import Any, Dict, List, Optional
import statistics

DEFAULT_THRESHOLDS = {
    "error_rate": 0.10,
    "latency_p95_ms": 800,
    "cpu_pct": 85,
    "memory_pct": 90,
    "db_wait_time_ms": 300,
    "queue_depth": 100,
}

def analyze_metrics(
    metric_events: List[Dict[str, Any]],
    thresholds: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Metrics Analysis Agent (V1): Detect threshold breaches + simple correlations.
    """
    if not metric_events:
        return {"anomalies": [], "correlations": []}

    thresholds = thresholds or DEFAULT_THRESHOLDS

    # Extract timeseries
    series: Dict[str, List[float]] = {k: [] for k in thresholds.keys()}
    ts_list: List[str] = []

    for ev in metric_events:
        ts_list.append(ev.get("ts", ""))
        m = ev.get("metrics", {})
        for k in series.keys():
            v = m.get(k)
            if isinstance(v, (int, float)):
                series[k].append(float(v))

    anomalies = []
    for k, vals in series.items():
        if not vals:
            continue
        last = vals[-1]
        thr = thresholds[k]
        if last >= thr:
            anomalies.append({
                "metric": k,
                "last_value": round(last, 4),
                "threshold": thr,
                "timestamp": ts_list[-1] if ts_list else None,
            })

    # Simple “correlations” (heuristic, not statistical)
    correlations = []
    if series["error_rate"] and series["db_wait_time_ms"]:
        if series["error_rate"][-1] >= thresholds["error_rate"] and series["db_wait_time_ms"][-1] >= thresholds["db_wait_time_ms"]:
            correlations.append("error_rate aligns with db_wait_time spike")

    if series["error_rate"] and series["latency_p95_ms"]:
        if series["error_rate"][-1] >= thresholds["error_rate"] and series["latency_p95_ms"][-1] >= thresholds["latency_p95_ms"]:
            correlations.append("error_rate aligns with latency p95 spike")

    if series["latency_p95_ms"] and series["cpu_pct"]:
        if series["latency_p95_ms"][-1] >= thresholds["latency_p95_ms"] and series["cpu_pct"][-1] >= thresholds["cpu_pct"]:
            correlations.append("latency spike aligns with high CPU")

    return {"anomalies": anomalies, "correlations": correlations}
