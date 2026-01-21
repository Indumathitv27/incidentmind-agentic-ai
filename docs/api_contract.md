# API Contract (V1)

## GET /health
Response 200:
{ "status": "ok" }

## POST /incidents/triage
Request:
{
  "alert": {
    "service": "orders-api",
    "severity": "critical",
    "timestamp": "2026-01-20T12:05:00Z",
    "signals": { "error_rate": 0.35, "latency_p95_ms": 1200 }
  },
  "options": { "time_window_minutes": 30 }
}

Response 200:
{
  "incident_id": "inc_0001",
  "incident_context": { },
  "log_findings": { },
  "metric_findings": { },
  "rca_hypothesis": { },
  "remediation_plan": { },
  "safety": { "blocked": false, "notes": [] }
}

Response 400:
{ "error": "Invalid alert payload" }
