# 🚨 IncidentMind — Agentic AI Incident Triage (FastAPI + Streamlit)

IncidentMind is an **Agentic AI–style incident triage platform** that ingests an alert payload, analyzes **real-time logs and metrics**, generates a **root-cause hypothesis (RCA)** with evidence, proposes a **safe remediation plan**, and persists every incident for retrieval and UI exploration.

Built to mirror **production AI systems**: API-first design, multi-agent orchestration, observability (`trace_id`), and safety guardrails.

---

## 🌐 Live Demo

- **Streamlit UI:** https://incidentmind-agentic-ai-triage.streamlit.app/
- **FastAPI Backend (Render):** https://incidentmind-agentic-ai.onrender.com
- **Swagger Docs:** https://incidentmind-agentic-ai.onrender.com/docs

---

## ✨ Key Features

### 🧠 Multi-Agent Pipeline
A modular agent chain with clear inputs/outputs:

1. **Alert Agent** → builds incident context, symptoms, category  
2. **Log Agent** → extracts dominant error patterns + correlated request IDs  
3. **Metrics Agent** → detects anomalies + correlations (e.g., latency vs CPU)  
4. **RCA Agent** → produces hypothesis + confidence + evidence + alternatives  
5. **Remediation Agent** → suggests prioritized remediation steps + validation checks  
6. **Safety Agent** → enforces safe, read-only behavior (no destructive actions)

### 🔎 Observability (Trace IDs)
Each triage request emits **structured JSON logs** at agent boundaries with a shared `trace_id` for end-to-end debugging.

### 💾 Persistent Incident Storage
Every triage run is stored as a JSON report and can be retrieved via `incident_id`.

### 🖥️ Streamlit UI
Run triage, view output sections, and browse incident history—all backed by the public API.

---

## 🧩 Architecture Overview

**Request Flow**
- Streamlit UI (or curl) → **FastAPI** → agent pipeline → storage → response

**Data Flow**
- Alert payload → incident context  
- Live logs + live metrics → findings  
- Findings → RCA hypothesis  
- RCA hypothesis → remediation plan  
- Output → safety check → stored report

---

## 🏗️ Architecture Diagram

```mermaid
flowchart LR
    U[User / SRE]
    ST[Streamlit UI]
    API[FastAPI Backend]

    U -->|UI actions| ST
    U -->|API calls| API
    ST -->|REST calls| API

    API -->|orchestrates| A1[Alert Agent]
    API -->|orchestrates| A2[Log Agent]
    API -->|orchestrates| A3[Metrics Agent]
    API -->|orchestrates| A4[RCA Agent]
    API -->|orchestrates| A5[Remediation Agent]
    API -->|enforces| A6[Safety Agent]

    A2 -->|reads logs| LOGS[(Live Logs)]
    A3 -->|reads metrics| METRICS[(Live Metrics)]

    LOGGEN[Log Generator] --> LOGS
    METGEN[Metrics Generator] --> METRICS

    API -->|stores report| STORE[(Incident Reports)]
    API -->|retrieves report| STORE

----

## 🔒 Safety & Guardrails (Read-Only Policy)

This system is intentionally **non-executing**:
- ✅ It *suggests* actions
- ❌ It does not run commands, mutate infrastructure, or trigger automated remediation

The **Safety Agent** adds policy notes and can block unsafe content if required.

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|-------:|----------|-------------|
| GET | `/health` | health check |
| POST | `/incidents/triage` | run triage pipeline and store report |
| GET | `/incidents/{incident_id}` | retrieve stored incident report |
| GET | `/incidents?limit=20` | list recent incidents (for UI history) |

---

## ▶️ Quickstart (Run Locally)

### 1) Setup Environment
```bash
git clone https://github.com/Indumathitv27/incidentmind-agentic-ai.git
cd incidentmind-agentic-ai

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
---

### 2) Start log & metric generators (real-time simulation)
Open two separate terminals

Terminal A
```bash
python scripts/log_generator.py
```
Terminal B
```bash
python scripts/metrics_generator.py
```

---

### 3) Start the FastAPI backend
```bash
uvicorn app.main:app --reload
```
-----

### 4) Start the Streamlit UI
```bash
streamlit run ui/streamlit_app.py
```

## 🚀 Why This Project Matters

This project demonstrates:
- Agentic AI system design
- API-first LLM application architecture
- Safety-aware AI development
- Observability in AI pipelines
- End-to-end deployment of production-style systems

