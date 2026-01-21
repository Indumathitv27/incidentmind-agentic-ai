# Agent Design (V1) — Incident Triage & RCA

## System Scope (V1)
- Input: alert JSON (service, severity, timestamp, signals)
- Output: incident report with RCA hypothesis + safe remediation plan
- V1 is read-only (no auto-fix)

## Agents (V1)

### 1) Alert Agent
**Goal:** classify incident and extract context  
**Input:** alert_json  
**Output:** incident_context JSON  
**Notes:** sets time window and category

### 2) Log Analysis Agent
**Goal:** find relevant error patterns in logs  
**Input:** incident_context + logs  
**Output:** log_findings JSON

### 3) Metrics Analysis Agent
**Goal:** detect anomalies in metrics during the time window  
**Input:** incident_context + metrics  
**Output:** metric_findings JSON

### 4) Root Cause Agent
**Goal:** correlate findings and propose RCA hypothesis  
**Input:** incident_context + log_findings + metric_findings  
**Output:** rca_hypothesis JSON (with confidence + alternatives)

### 5) Remediation Agent
**Goal:** propose safe remediation steps + validation checks  
**Input:** rca_hypothesis  
**Output:** remediation_plan JSON

### 6) Safety Agent
**Goal:** prevent unsafe actions / prompt injection & sanitize output  
**Input:** all intermediate + final outputs  
**Output:** approved_final_report OR blocked response

## UI (Streamlit)
- Streamlit app collects alert JSON + options (time window)
- Calls FastAPI endpoints:
  - GET /health
  - POST /incidents/triage
- Displays:
  - incident_context
  - findings (logs/metrics)
  - rca_hypothesis
  - remediation_plan
  - safety notes
