import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta
from fitparse import FitFile
import google.generativeai as genai

# 1. Setup (Key holst du dir gratis bei Google AI Studio)
genai.configure(api_key="api-key-hier")
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_insight(activity_df, metrics):
    if activity_df.empty:
        return "Noch keine Daten für eine Analyse vorhanden."

    last_act = activity_df.iloc[-1]
    
    # Wir bauen ein "Gedächtnis" für die KI
    context = f"""
    Du bist ein Triathlon-Experte. Hier sind die Daten meines Athleten:
    - Sportart: {last_act['sport']}
    - Dauer: {last_act['duration']} min
    - Puls: {last_act['avg_hr']} bpm
    - Aktuelle Fitness (CTL): {metrics.iloc[-1]['CTL']:.1f}
    - Aktuelle Form (TSB): {metrics.iloc[-1]['TSB']:.1f}
    
    Schreibe eine kurze, intelligente Analyse (3-4 Sätze). 
    Sag ihm nicht nur was er gemacht hat, sondern was das für seine Form bedeutet 
    und was er morgen trainieren oder essen sollte. Sei präzise.
    """
    
    try:
        response = model.generate_content(context)
        return response.text
    except Exception as e:
        return f"KI-Analyse aktuell nicht verfügbar: {e}"

# --- DATENBANK FUNKTIONEN ---
def init_db():
    conn = sqlite3.connect('triathlon_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS activities 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, sport TEXT, duration INTEGER, 
                  avg_hr INTEGER, tss REAL, source TEXT)''')
    conn.commit()
    return conn

def save_activity(date, sport, duration, avg_hr, tss, source="manual"):
    conn = sqlite3.connect('triathlon_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO activities (date, sport, duration, avg_hr, tss, source) VALUES (?, ?, ?, ?, ?, ?)",
              (date, sport, duration, avg_hr, tss, source))
    conn.commit()
    conn.close()

def load_activities():
    conn = sqlite3.connect('triathlon_data.db')
    df = pd.read_sql_query("SELECT * FROM activities ORDER BY date ASC", conn)
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

# --- BERECHNUNG DER METRIKEN (CTL, ATL, TSB) ---
def calculate_metrics(df):
    if df.empty:
        return None
    
    # Wir erstellen einen lückenlosen Zeitstrahl vom ersten Training bis heute
    start_date = df['date'].min()
    end_date = datetime.now()
    idx = pd.date_range(start_date, end_date)
    
    # TSS pro Tag summieren
    daily_tss = df.groupby('date')['tss'].sum().reindex(idx, fill_value=0)
    
    # Banister Modell (Exponential Moving Average)
    ctl = daily_tss.ewm(span=42, adjust=False).mean()
    atl = daily_tss.ewm(span=7, adjust=False).mean()
    tsb = ctl.shift(1) - atl.shift(1) # Form von gestern für heute
    
    return pd.DataFrame({'CTL': ctl, 'ATL': atl, 'TSB': tsb, 'TSS': daily_tss}, index=idx)

# --- UI SETUP ---
st.set_page_config(page_title="AI Triathlon Coach Pro", layout="wide")
init_db()
activities_df = load_activities()

st.title("🏆 Triathlon Performance Center")

# --- SIDEBAR: NEUES TRAINING ---
st.sidebar.header("➕ Training hinzufügen")
with st.sidebar.expander("Manuelle Eingabe"):
    date_input = st.date_input("Datum", datetime.now())
    sport_input = st.selectbox("Sportart", ["Rad", "Lauf", "Schwimmen"])
    dur_input = st.number_input("Dauer (min)", 10, 500, 60)
    hr_input = st.number_input("Puls (ø)", 80, 200, 140)
    
    # Einfache TSS Schätzung (Intelligenz-Faktor)
    # Formel: (Dauer * Puls * Intensitätsfaktor) / (Schwelle * 60) * 100
    # Hier vereinfacht:
    lthr_user = 170 
    tss_calc = (dur_input * hr_input * (hr_input/lthr_user)) / (lthr_user * 60) * 100
    
    if st.button("Training speichern"):
        save_activity(date_input.strftime("%Y-%m-%d"), sport_input, dur_input, hr_input, tss_calc)
        st.success("Gespeichert!")
        st.rerun()

st.sidebar.divider()

# --- INTELLIGENTER FIT-UPLOAD ---
st.sidebar.subheader("⌚ .FIT Datei hochladen")
fit_file = st.sidebar.file_uploader("Garmin/Wahoo Datei", type=["fit"])

if fit_file:
    try:
        fitfile = FitFile(fit_file)
        
        # 1. Aktivitätstyp erkennen
        detected_sport = "Unbekannt"
        for message in fitfile.get_messages('sport'):
            for data in message:
                if data.name == 'name':
                    detected_sport = data.value.capitalize()
        
        # Falls nichts gefunden wurde, über die Messages raten
        if detected_sport == "Unbekannt":
            # Suche nach Rad-spezifischen Daten wie 'power' oder 'cadence'
            has_power = any(msg.name == 'record' and 'power' in [d.name for d in msg] for msg in fitfile.get_messages('record'))
            detected_sport = "Rad" if has_power else "Lauf"

        # 2. Daten extrahieren (Puls, Geschwindigkeit, Trittfrequenz)
        records = []
        for record in fitfile.get_messages('record'):
            r_data = {m.name: m.value for m in record}
            records.append(r_data)
        
        df_temp = pd.DataFrame(records)
        
        if not df_temp.empty:
            # Metriken berechnen
            avg_hr = df_temp['heart_rate'].mean() if 'heart_rate' in df_temp else 0
            avg_speed = df_temp['speed'].mean() * 3.6 if 'speed' in df_temp else 0 # m/s zu km/h
            max_speed = df_temp['speed'].max() * 3.6 if 'speed' in df_temp else 0
            avg_cadence = df_temp['cadence'].mean() if 'cadence' in df_temp else 0
            
            duration_min = (df_temp['timestamp'].max() - df_temp['timestamp'].min()).seconds / 60
            date_str = df_temp['timestamp'].min().strftime("%Y-%m-%d")
            
            # TSS Schätzung
            lthr_user = 170 
            tss_fit = (duration_min * avg_hr * (avg_hr/lthr_user)) / (lthr_user * 60) * 100
            
            # Feedback-Anzeige vor dem Speichern
            st.sidebar.success(f"Erkannt: **{detected_sport}**")
            
            # Spezielles Feedback je nach Sportart
            if detected_sport == "Rad":
                st.sidebar.write(f"🚴 Speed: {round(avg_speed, 1)} km/h")
                st.sidebar.write(f"🔄 Trittfrequenz: {round(avg_cadence)} rpm")
            else:
                pace = 60 / avg_speed if avg_speed > 0 else 0
                st.sidebar.write(f"🏃 Pace: {round(pace, 2)} min/km")
            
            if st.sidebar.button("Einheit final speichern"):
                save_activity(date_str, detected_sport, int(duration_min), int(avg_hr), tss_fit, source="FIT-File")
                st.success("Training in die Datenbank übernommen!")
                st.rerun()
                
    except Exception as e:
        st.sidebar.error(f"Fehler beim Parsen: {e}")

# --- HAUPTANSICHT ---
# --- HAUPTANSICHT ---
if not activities_df.empty:
    metrics = calculate_metrics(activities_df)
    
    st.divider()
    st.subheader("🤖 Dein AI Coach Insights")

# Hier rufen wir die Funktion auf und zeigen das Ergebnis an
    with st.spinner("KI analysiert deine Form..."):
        insight = get_ai_insight(activities_df, metrics)
        st.write(insight)

    # Aktuelle Werte (Letzter Tag im berechneten Zeitstrahl)
    last_day = metrics.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("Fitness (CTL)", round(last_day['CTL'], 1))
    c2.metric("Ermüdung (ATL)", round(last_day['ATL'], 1), delta_color="inverse")
    c3.metric("Form (TSB)", round(last_day['TSB'], 1))

    # Grafiken
    st.subheader("📈 Langzeit-Analyse")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(metrics.index, metrics['CTL'], label="Fitness (Belastbarkeit)", color="blue")
    ax.fill_between(metrics.index, metrics['TSB'], 0, alpha=0.2, color="green", label="Form")
    ax.set_ylabel("Belastungspunkte")
    ax.legend()
    st.pyplot(fig)

    # --- EINZELANSICHT AKTIVITÄTEN ---
    st.divider()
    st.subheader("🔍 Aktivitäts-Archiv & Analyse")

    # KORREKTUR: Datum in String umwandeln für das Label
    activities_df['date_str'] = activities_df['date'].dt.strftime('%Y-%m-%d')
    activities_df['label'] = activities_df['date_str'] + " - " + activities_df['sport']
    
    selected_label = st.selectbox("Wähle eine Einheit zur Detailanalyse:", activities_df['label'].iloc[::-1])
    
    # Die gewählte Aktivität filtern
    selected_act = activities_df[activities_df['label'] == selected_label].iloc[0]
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Typ", selected_act['sport'])
    with col_b:
        st.metric("Belastung (TSS)", f"{round(selected_act['tss'], 1)}")
    with col_c:
        # Schätzung kcal
        kcal_rate = 10 if selected_act['sport'] == "Lauf" else 7
        kcal_est = selected_act['duration'] * kcal_rate
        st.metric("Geschätzte kcal", f"~{int(kcal_est)}")

    # Graph-Erklärung
    current_ctl = last_day['CTL'] if last_day['CTL'] > 0 else 1
    impact = round(selected_act['tss']/42, 2)
    st.info(f"**Analyse:** Diese Einheit hatte einen Belastungswert von {round(selected_act['tss'],1)}. "
            f"Das steigerte deine langfristige Fitness (CTL) theoretisch um {impact} Punkte.")

    # --- ERNÄHRUNGS-ASSISTENT ---
    st.subheader("🍎 Nutrition & Recovery")
    with st.expander("Was sollte ich nach dieser Einheit essen?"):
        if selected_act['duration'] > 90:
            st.warning("⚠️ **Hoher Glykogen-Verlust:** Fülle deine Kohlenhydrate schnell auf (Pasta, Reis, Bananen).")
        elif selected_act['tss'] > 80:
            st.info("🔥 **Hoher Stress:** Achte auf 20-30g Protein zur Muskelregeneration.")
        else:
            st.success("✅ **Moderate Einheit:** Eine normale, ausgewogene Mahlzeit ist ausreichend.")

    # --- DETAIL-VISUALISIERUNG ---
    st.divider()
    st.subheader(f"🧐 Intensitäts-Check: {selected_act['sport']}")
    
    chart_data = pd.DataFrame(
        np.random.normal(selected_act['avg_hr'], 3, int(selected_act['duration'])),
        columns=['Herzfrequenz (simuliert)']
    )
    st.line_chart(chart_data)

else:
    st.info("Noch keine Trainingsdaten vorhanden. Füge dein erstes Training in der Sidebar hinzu!")