from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents.alert_agent import build_incident_context
from agents.log_agent import analyze_logs
from agents.metrics_agent import analyze_metrics
from agents.rca_agent import build_rca_hypothesis
from agents.remediation_agent import build_remediation_plan
from agents.safety_agent import safety_check

from tools.logs import fetch_logs
from tools.metrics import fetch_metrics
from tools.storage import new_incident_id, save_report, load_report
from tools.observability import new_trace_id, log_event

app = FastAPI(title="IncidentMind API", version="0.1.0")


# ---------- Schemas (V1) ----------
class AlertPayload(BaseModel):
    service: str = Field(..., examples=["orders-api"])
    severity: str = Field(..., examples=["critical"])
    timestamp: str = Field(..., examples=["2026-01-20T12:05:00Z"])
    signals: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TriageOptions(BaseModel):
    time_window_minutes: int = Field(30, ge=5, le=240)
    include_raw_logs: bool = False
    include_raw_metrics: bool = False


class TriageRequest(BaseModel):
    alert: AlertPayload
    options: Optional[TriageOptions] = TriageOptions()


# ---------- Routes ----------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/incidents/triage")
def triage_incident(req: TriageRequest):
    # Basic validation
    if not req.alert.service or not req.alert.severity or not req.alert.timestamp:
        raise HTTPException(status_code=400, detail="Invalid alert payload")

    incident_id = new_incident_id()
    trace_id = new_trace_id()

    log_event(
        "triage_request_received",
        trace_id,
        {"service": req.alert.service, "severity": req.alert.severity, "timestamp": req.alert.timestamp},
    )

    # ---- Alert Agent
    mock_incident_context = build_incident_context(
        service=req.alert.service,
        severity=req.alert.severity,
        time_window_minutes=req.options.time_window_minutes,
        signals=req.alert.signals or {},
    )
    log_event(
        "alert_agent_done",
        trace_id,
        {
            "category": mock_incident_context.get("category"),
            "symptoms": mock_incident_context.get("symptoms"),
        },
    )

    # ---- Log Agent
    log_lines = fetch_logs(req.alert.service)
    mock_log_findings = analyze_logs(log_lines)
    log_event(
        "log_agent_done",
        trace_id,
        {"top_errors": mock_log_findings.get("top_errors", [])[:3]},
    )

    # ---- Metrics Agent
    metric_events = fetch_metrics(req.alert.service, limit=120)
    mock_metric_findings = analyze_metrics(metric_events)
    log_event(
        "metrics_agent_done",
        trace_id,
        {
            "anomalies": mock_metric_findings.get("anomalies", []),
            "correlations": mock_metric_findings.get("correlations", []),
        },
    )

    # ---- RCA Agent
    mock_rca_hypothesis = build_rca_hypothesis(
        mock_incident_context,
        mock_log_findings,
        mock_metric_findings,
    )
    log_event(
        "rca_agent_done",
        trace_id,
        {
            "root_cause": mock_rca_hypothesis.get("root_cause"),
            "confidence": mock_rca_hypothesis.get("confidence"),
        },
    )

    # ---- Remediation Agent
    mock_remediation_plan = build_remediation_plan(
        mock_rca_hypothesis,
        mock_incident_context,
    )
    log_event(
        "remediation_agent_done",
        trace_id,
        {"steps_count": len(mock_remediation_plan.get("recommended_steps", []))},
    )

    # ---- Report object (stored + returned)
    report = {
        "incident_id": incident_id,
        "trace_id": trace_id,
        "incident_context": mock_incident_context,
        "log_findings": mock_log_findings,
        "metric_findings": mock_metric_findings,
        "rca_hypothesis": mock_rca_hypothesis,
        "remediation_plan": mock_remediation_plan,
    }

    # ---- Safety Agent
    safety = safety_check(report)
    log_event("safety_check_done", trace_id, {"blocked": safety.get("blocked", False)})

    # If blocked -> return minimal safe response AND store it
    if safety.get("blocked"):
        blocked_report = {
            "incident_id": incident_id,
            "trace_id": trace_id,
            "incident_context": mock_incident_context,
            "log_findings": {},
            "metric_findings": {},
            "rca_hypothesis": {
                "root_cause": "Blocked by safety policy",
                "confidence": 0.0,
                "evidence": [],
                "alternatives": [],
            },
            "remediation_plan": {
                "recommended_steps": [],
                "validation": [],
                "notes": ["Output blocked due to safety policy."],
            },
            "safety": safety,
        }
        stored = save_report(incident_id, blocked_report)
        return stored

    # Normal response: attach safety, store, return storage envelope
    final_payload = {**report, "safety": safety}
    stored = save_report(incident_id, final_payload)
    return stored


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    data = load_report(incident_id)
    if not data:
        raise HTTPException(status_code=404, detail="Incident not found")
    return data


@app.get("/incidents")
def list_incidents(limit: int = 20):
    report_dir = Path(__file__).resolve().parents[1] / "outputs" / "incident_reports"
    if not report_dir.exists():
        return {"incidents": []}

    files = sorted(report_dir.glob("inc_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    items = []
    for p in files[:limit]:
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
            items.append(
                {
                    "incident_id": payload.get("incident_id"),
                    "created_at": payload.get("created_at"),
                }
            )
        except Exception:
            continue

    return {"incidents": items}
