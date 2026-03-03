from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
import random

# ----------------------------
# 1️⃣ Trainingsdaten simulieren
# ----------------------------
num_trainings = 250
sports = ["Rad", "Lauf", "Schwimmen"]

trainings = []
fitness = {sport: 0 for sport in sports}
fatigue = {sport: 0 for sport in sports}

fitness_values = []
fatigue_values = []
performance_values = []
training_types = []

for i in range(num_trainings):
    sport = random.choice(sports)
    hr = random.randint(140, 180)
    duration = random.randint(20, 90)  # Minuten
    load = 0.5*hr + 0.3*duration
    sport_factor = {"Rad":1.0, "Lauf":0.8, "Schwimmen":0.6}[sport]

    # Fitness / Fatigue aktualisieren
    fitness[sport] = fitness[sport]*0.95 + load*0.05*sport_factor
    fatigue[sport] = fatigue[sport]*0.85 + load*0.15*sport_factor

    total_fitness = sum(fitness.values())
    total_fatigue = sum(fatigue.values())
    performance = total_fitness - total_fatigue + random.uniform(-2,2)

    # Trainingsanalyse
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
        "hr": hr,
        "duration": duration,
        "sport": sport,
        "fitness": total_fitness,
        "fatigue": total_fatigue,
        "performance": performance,
        "type": t_type,
        "benefit": benefit
    })

    fitness_values.append(total_fitness)
    fatigue_values.append(total_fatigue)
    performance_values.append(performance)
    training_types.append(t_type)

# ----------------------------
# 2️⃣ Analyse heutiges Training
# ----------------------------
hr_today = 165
duration_today = 50
sport_today = "Rad"

load_today = 0.5*hr_today + 0.3*duration_today
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

# Überlastung/Unterforderung Logik
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
print(f"Kommentar: {load_comment}")

# ----------------------------
# 4️⃣ ML-Modell optional (Performance Vorhersage)
# ----------------------------
X = np.array([[t["hr"], t["duration"], t["fitness"], t["fatigue"]] for t in trainings])
y = np.array([t["performance"] for t in trainings])
model = LinearRegression()
model.fit(X, y)
score = model.score(X, y)
print("ML R² Score (Performance-Modell):", round(score,3))

# ----------------------------
# 5️⃣ Grafische Darstellung
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