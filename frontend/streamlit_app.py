from datetime import datetime
import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_BASE = (
    st.secrets.get("API_BASE")
    or os.getenv("API_BASE")
    or "http://127.0.0.1:8000/api"
).rstrip("/")


def api_get(path: str, timeout: int = 10):
    try:
        return requests.get(f"{API_BASE}{path}", timeout=timeout)
    except requests.RequestException as exc:
        st.error(f"API nicht erreichbar unter {API_BASE}: {exc}")
        return None


def api_post(path: str, payload: dict, timeout: int = 10):
    try:
        return requests.post(f"{API_BASE}{path}", json=payload, timeout=timeout)
    except requests.RequestException as exc:
        st.error(f"API nicht erreichbar unter {API_BASE}: {exc}")
        return None

st.set_page_config(page_title="AthleticInsights", layout="wide")
st.title("AthleticInsights - AI Coach MVP")
st.caption(f"API Base: {API_BASE}")

st.sidebar.header("Neue Einheit")
with st.sidebar.form("activity_form"):
    date_value = st.date_input("Datum", datetime.now())
    sport = st.selectbox("Sport", ["Rad", "Lauf", "Schwimmen"])
    duration = st.number_input("Dauer (Min)", min_value=1, max_value=1440, value=60)
    avg_hr = st.number_input("Durchschnittspuls", min_value=40, max_value=230, value=145)
    custom_tss = st.number_input("TSS (optional, 0 = automatisch)", min_value=0.0, value=0.0)
    submitted = st.form_submit_button("Speichern")

if submitted:
    payload = {
        "date": date_value.isoformat(),
        "sport": sport,
        "duration": int(duration),
        "avg_hr": int(avg_hr),
        "source": "manual",
    }
    if custom_tss > 0:
        payload["tss"] = float(custom_tss)

    response = api_post("/activities", payload)
    if response is not None and response.ok:
        st.sidebar.success("Einheit gespeichert")
    elif response is not None:
        st.sidebar.error(f"Fehler: {response.text}")

col1, col2, col3 = st.columns(3)

metrics_res = api_get("/metrics")
insight_res = api_get("/insight")
activities_res = api_get("/activities")

if metrics_res is not None and metrics_res.ok:
    metrics = metrics_res.json()
    col1.metric("CTL", round(metrics["ctl"], 1))
    col2.metric("ATL", round(metrics["atl"], 1), delta_color="inverse")
    col3.metric("TSB", round(metrics["tsb"], 1))
elif metrics_res is not None:
    st.error(f"Metrics-Endpoint antwortet mit {metrics_res.status_code}: {metrics_res.text}")

if insight_res is not None and insight_res.ok:
    st.info(insight_res.json().get("message", "Keine Insight verfuegbar"))

if activities_res is not None and activities_res.ok:
    rows = activities_res.json()
    if rows:
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])

        st.subheader("Aktivitaeten")
        st.dataframe(df.sort_values(["date", "id"], ascending=False), use_container_width=True)

        daily = df.groupby("date", as_index=False)["tss"].sum()
        fig = px.line(daily, x="date", y="tss", title="TSS pro Tag")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Noch keine Aktivitaeten vorhanden.")
elif activities_res is not None:
    st.error("Backend nicht erreichbar. Starte zuerst FastAPI.")
