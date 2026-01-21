import json
import requests
import streamlit as st
import os

API_BASE = os.getenv("INCIDENTMIND_API_URL", "http://127.0.0.1:8000")


st.set_page_config(page_title="IncidentMind", layout="wide")
st.title("IncidentMind — Agentic Incident Triage")
st.caption("Streamlit UI → FastAPI → Agents (Logs, Metrics, RCA, Remediation, Safety)")

# ---------- Sidebar: Incident History ----------
with st.sidebar:
    st.header("Incident History")
    limit = st.slider("Show last N incidents", 5, 50, 15)

    incidents = []
    try:
        r = requests.get(f"{API_BASE}/incidents", params={"limit": limit}, timeout=5)
        incidents = r.json().get("incidents", [])
    except Exception:
        st.warning("Could not load incident list. Is FastAPI running?")

    selected_id = st.selectbox(
        "Select an incident_id to view",
        options=[""] + [i["incident_id"] for i in incidents if i.get("incident_id")],
    )

    if selected_id:
        try:
            r = requests.get(f"{API_BASE}/incidents/{selected_id}", timeout=10)
            st.success("Loaded incident")
            st.json(r.json())
        except Exception as e:
            st.error(f"Failed to load incident: {e}")

# ---------- Main: Run Triage ----------
st.subheader("Run Triage")

default_alert = {
    "service": "orders-api",
    "severity": "critical",
    "timestamp": "2026-01-20T12:05:00Z",
    "signals": {"error_rate": 0.35, "latency_p95_ms": 1200},
}

col1, col2 = st.columns(2)

with col1:
    alert_text = st.text_area(
        "Alert JSON",
        value=json.dumps(default_alert, indent=2),
        height=260,
    )

with col2:
    time_window = st.number_input("Time window (minutes)", min_value=5, max_value=240, value=30, step=5)

if st.button("Run /incidents/triage"):
    try:
        alert_obj = json.loads(alert_text)
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e}")
        st.stop()

    payload = {
        "alert": alert_obj,
        "options": {"time_window_minutes": int(time_window)},
    }

    try:
        r = requests.post(f"{API_BASE}/incidents/triage", json=payload, timeout=30)
        if r.status_code != 200:
            st.error(f"API error {r.status_code}: {r.text}")
        else:
            data = r.json()
            st.success(f"Stored incident: {data.get('incident_id')} at {data.get('created_at')}")

            report = data.get("report", {})
            st.subheader("Incident Context")
            st.json(report.get("incident_context", {}))

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Log Findings")
                st.json(report.get("log_findings", {}))
            with c2:
                st.subheader("Metric Findings")
                st.json(report.get("metric_findings", {}))

            st.subheader("RCA Hypothesis")
            st.json(report.get("rca_hypothesis", {}))

            st.subheader("Remediation Plan")
            st.json(report.get("remediation_plan", {}))

            st.subheader("Safety")
            st.json(report.get("safety", {}))

    except Exception as e:
        st.error(f"Failed to call API: {e}")
