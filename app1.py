import random
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# 1️⃣ Trainingsdaten simulieren
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
        elevation = random.randint(0, 500)  # Höhenmeter
        load = 0.5*hr + 0.3*duration + 0.2*watt/2
    elif sport == "Lauf":
        pace = round(random.uniform(4.0, 6.0),2)  # min/km
        steps = random.randint(160, 200)
        distance = round(duration/60*10,1)  # grobe Distanz in km
        load = 0.5*hr + 0.3*duration + 0.2*distance*10
    elif sport == "Schwimmen":
        pace_100m = round(random.uniform(1.4, 2.0),2)  # min/100m
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
        # Sport-spezifische Metriken
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
# 2️⃣ Analyse heutiges Training (Beispiel Rad)
# ----------------------------
sport_today = "Rad"
duration_today = 50
hr_today = 165
watt_today = 210
cadence_today = 90
speed_today = 32
elevation_today = 300

load_today = 0.5*hr_today + 0.3*duration_today + 0.2*watt_today/2
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
# 3️⃣ Ausgabe
# ----------------------------
print(f"Heute: {sport_today}, Dauer: {duration_today} min, HR: {hr_today}")
print(f"Fitness: {round(total_fitness_today,1)}, Fatigue: {round(total_fatigue_today,1)}, Performance: {round(performance_today,1)}")
print(f"Trainingsart: {type_today}, Nutzen: {benefit_today}")
print(f"Watt: {watt_today}, Trittfrequenz: {cadence_today}, Geschwindigkeit: {speed_today} km/h, Höhenmeter: {elevation_today}")
print(f"Kommentar: {load_comment}")

# ----------------------------
# 4️⃣ Grafische Darstellung
# ----------------------------
plt.figure(figsize=(12,5))
plt.plot(fitness_values, label="Fitness")
plt.plot(fatigue_values, label="Fatigue")
plt.plot(performance_values, label="Performance")
plt.axhline(y=performance_today, color='r', linestyle='--', label='Heute')
plt.xlabel("Trainingseinheit")
plt.ylabel("Werte")
plt.title("Fitness-Fatigue-Performance Verlauf & heutige Analyse")
plt.legend()
plt.show()