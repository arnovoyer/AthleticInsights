# Speichere das z.B. als triathlon_app.py und führe aus mit: streamlit run triathlon_app.py

import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Triathlon Training Analyzer", layout="wide")

st.title("🏊🚴‍♂️🏃 Triathlon Training Analyzer")

# ----------------------------
# Simulierte Trainingsdaten
# ----------------------------
num_trainings = 200
sports = ["Rad", "Lauf", "Schwimmen"]

trainings = []
fitness = {sport: 0 for sport in sports}
fatigue = {sport: 0 for sport in sports}

fitness_values = []
fatigue_values = []
performance_values = []

for i in range(num_trainings):
    sport = random.choice(sports)
    duration = random.randint(20, 90)  # Minuten
    hr = random.randint(140, 180)

    if sport == "Rad":
        watt = random.randint(150, 250)
        cadence = random.randint(70, 100)
        speed = round(random.uniform(25, 40), 1)
        elevation = random.randint(0, 500)
        load = 0.5*hr + 0.3*duration + 0.2*watt/2
    elif sport == "Lauf":
        pace = round(random.uniform(4.0, 6.0),2)  # min/km
        steps = random.randint(160, 200)
        distance = round(duration/60*10,1)
        load = 0.5*hr + 0.3*duration + 0.2*distance*10
    elif sport == "Schwimmen":
        pace_100m = round(random.uniform(1.4, 2.0),2)
        distance = random.randint(500, 2000)
        load = 0.5*hr + 0.3*duration + 0.2*distance/10

    sport_factor = {"Rad":1.0, "Lauf":0.8, "Schwimmen":0.6}[sport]
    fitness[sport] = fitness[sport]*0.95 + load*0.05*sport_factor
    fatigue[sport] = fatigue[sport]*0.85 + load*0.15*sport_factor
    total_fitness = sum(fitness.values())
    total_fatigue = sum(fatigue.values())
    performance = total_fitness - total_fatigue + random.uniform(-2,2)

    # Trainingsart
    if duration <= 40 and hr >= 160:
        t_type = "Intervalle"
        benefit = "Anaerobe Schwelle"
    elif duration > 60 and hr < 160:
        t_type = "Dauertraining"
        benefit = "Grundlagenausdauer"
    elif hr < 150:
        t_type = "Regeneration"
        benefit = "Erholung"
    else:
        t_type = "Normales Training"
        benefit = "Allgemein"

    trainings.append({
        "sport": sport,
        "duration": duration,
        "hr": hr,
        "fitness": total_fitness,
        "fatigue": total_fatigue,
        "performance": performance,
        "type": t_type,
        "benefit": benefit,
        "watt": watt if sport=="Rad" else None,
        "cadence": cadence if sport=="Rad" else None,
        "speed": speed if sport=="Rad" else None,
        "elevation": elevation if sport=="Rad" else None,
        "pace": pace if sport=="Lauf" else None,
        "steps": steps if sport=="Lauf" else None,
        "distance": distance if sport in ["Lauf","Schwimmen"] else None,
        "pace_100m": pace_100m if sport=="Schwimmen" else None
    })

    fitness_values.append(total_fitness)
    fatigue_values.append(total_fatigue)
    performance_values.append(performance)

# ----------------------------
# Streamlit Inputs
# ----------------------------
st.sidebar.header("Heutiges Training")
sport_today = st.sidebar.selectbox("Sportart", sports)
duration_today = st.sidebar.slider("Dauer (min)", 20, 120, 60)
hr_today = st.sidebar.slider("Durchschnittliche Herzfrequenz", 120, 190, 160)

# Sport-spezifische Eingaben
if sport_today == "Rad":
    watt_today = st.sidebar.slider("Watt", 100, 300, 200)
    cadence_today = st.sidebar.slider("Trittfrequenz", 60, 120, 90)
    speed_today = st.sidebar.slider("Geschwindigkeit (km/h)", 15, 50, 30)
    elevation_today = st.sidebar.slider("Höhenmeter", 0, 1000, 200)
elif sport_today == "Lauf":
    pace_today = st.sidebar.slider("Pace (min/km)", 3.0, 7.0, 5.0)
    steps_today = st.sidebar.slider("Schrittfrequenz", 140, 210, 180)
    distance_today = round(duration_today/60*10,1)
elif sport_today == "Schwimmen":
    pace_100m_today = st.sidebar.slider("Zeit pro 100m (min)", 1.2, 2.5, 1.8)
    distance_today = st.sidebar.slider("Distanz (m)", 200, 2500, 1000)

# ----------------------------
# Analyse
# ----------------------------
load_today = 0
if sport_today=="Rad":
    load_today = 0.5*hr_today + 0.3*duration_today + 0.2*watt_today/2
elif sport_today=="Lauf":
    load_today = 0.5*hr_today + 0.3*duration_today + 0.2*distance_today*10
elif sport_today=="Schwimmen":
    load_today = 0.5*hr_today + 0.3*duration_today + 0.2*distance_today/10

sport_factor = {"Rad":1.0, "Lauf":0.8, "Schwimmen":0.6}[sport_today]
fitness[sport_today] = fitness[sport_today]*0.95 + load_today*0.05*sport_factor
fatigue[sport_today] = fatigue[sport_today]*0.85 + load_today*0.15*sport_factor

total_fitness_today = sum(fitness.values())
total_fatigue_today = sum(fatigue.values())
performance_today = total_fitness_today - total_fatigue_today + random.uniform(-2,2)

# Trainingsart & Nutzen
if duration_today <= 40 and hr_today >= 160:
    type_today = "Intervalle"
    benefit_today = "Anaerobe Schwelle"
elif duration_today > 60 and hr_today < 160:
    type_today = "Dauertraining"
    benefit_today = "Grundlagenausdauer"
elif hr_today < 150:
    type_today = "Regeneration"
    benefit_today = "Erholung"
else:
    type_today = "Normales Training"
    benefit_today = "Allgemein"

perf_avg = np.mean(performance_values)
if performance_today > perf_avg + 5:
    load_comment = "Sehr intensive Einheit – gute Belastung"
elif performance_today < perf_avg - 5:
    load_comment = "Leichte Einheit – evtl. Unterforderung oder Regeneration"
else:
    load_comment = "Normal intensive Einheit"

# ----------------------------
# Ausgabe
# ----------------------------
st.subheader("Heutige Trainingseinheit")
st.write(f"**Sportart:** {sport_today} | **Dauer:** {duration_today} min | **HR:** {hr_today}")
st.write(f"**Fitness:** {round(total_fitness_today,1)}, **Fatigue:** {round(total_fatigue_today,1)}, **Performance:** {round(performance_today,1)}")
st.write(f"**Trainingsart:** {type_today} | **Nutzen:** {benefit_today}")
st.write(f"**Kommentar:** {load_comment}")

if sport_today=="Rad":
    st.write(f"Watt: {watt_today}, Trittfrequenz: {cadence_today}, Geschwindigkeit: {speed_today} km/h, Höhenmeter: {elevation_today}")
elif sport_today=="Lauf":
    st.write(f"Pace: {pace_today} min/km, Schritte: {steps_today}, Distanz: {distance_today} km")
elif sport_today=="Schwimmen":
    st.write(f"Pace pro 100m: {pace_100m_today} min, Distanz: {distance_today} m")

# ----------------------------
# Grafik
# ----------------------------
st.subheader("📈 Fitness-Fatigue-Performance Verlauf")
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(fitness_values, label="Fitness")
ax.plot(fatigue_values, label="Fatigue")
ax.plot(performance_values, label="Performance")
ax.axhline(y=performance_today, color='r', linestyle='--', label='Heute')
ax.set_xlabel("Trainingseinheit")
ax.set_ylabel("Werte")
ax.set_title("Fitness-Fatigue-Performance Verlauf & heutige Analyse")
ax.legend()
st.pyplot(fig)