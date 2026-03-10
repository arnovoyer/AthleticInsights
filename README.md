# AthleticInsights MVP

Diese Version trennt die App in Schichten:

- Frontend: Streamlit UI
- Backend: FastAPI API
- Database: SQLite im MVP (spaeter PostgreSQL/Supabase)

## Projektstruktur

- `frontend/streamlit_app.py`: UI fuer Eingabe, Metriken und Insight
- `backend/main.py`: FastAPI Einstiegspunkt
- `backend/api/routes.py`: API Endpunkte
- `backend/services/metrics.py`: CTL/ATL/TSB und TSS Logik
- `backend/services/insights.py`: Coach-Interpretation
- `backend/db/repository.py`: Persistenz-Schicht

## Quickstart

1. Virtuelle Umgebung aktivieren (falls noch nicht aktiv)
2. Abhaengigkeiten installieren:

```powershell
pip install -r requirements.txt
```

3. Backend starten:

```powershell
uvicorn backend.main:app --reload
```

4. Neues Terminal und Frontend starten:

```powershell
streamlit run frontend/streamlit_app.py
```

## API Endpunkte

- `GET /api/health`
- `POST /api/activities`
- `GET /api/activities`
- `GET /api/metrics`
- `GET /api/insight`

## Naechste Schritte Richtung Strava Active Intelligence

1. DB auf Supabase/PostgreSQL migrieren (Repository austauschen, API bleibt gleich).
2. OAuth + Webhooks fuer Garmin/Strava im Backend ergaenzen.
3. Hintergrundjobs (z. B. Celery/Redis oder FastAPI BackgroundTasks) fuer Ingestion und Analyse.
4. RAG Layer hinzufuegen: Sessions/Trainings als Embeddings speichern und semantisch abrufbar machen.
5. Proaktive Alerts: Regelwerk + Agent, der TSB, HR Drift und Planabweichungen ueberwacht.
