from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
import random

# ----------------------------
# 1️⃣ Simulierte Trainingsdaten
# ----------------------------
num_trainings = 300
trainings = []
fitness = 0
fatigue = 0

fitness_values = []
fatigue_values = []

# zuerst Rohwerte sammeln
for i in range(num_trainings):
    hr = random.randint(145, 185)
    duration = random.randint(30, 70)

    load = 0.5*hr + 0.3*duration

    fitness = fitness * 0.95 + load * 0.05
    fatigue = fatigue * 0.8 + load * 0.2

    fitness_values.append(fitness)
    fatigue_values.append(fatigue)

# ----------------------------
# 2️⃣ Fitness/Fatigue normalisieren
# ----------------------------
fitness_max = max(fitness_values)
fatigue_max = max(fatigue_values)

fitness_scaled = [f / fitness_max * 10 for f in fitness_values]
fatigue_scaled = [f / fatigue_max * 10 for f in fatigue_values]

performance_values = [f - fa for f, fa in zip(fitness_scaled, fatigue_scaled)]

# ----------------------------
# 3️⃣ Watt simulieren
# ----------------------------
watt_values = []
trainings = []

for i in range(num_trainings):
    hr = random.randint(145, 185)
    duration = random.randint(30, 70)
    perf = performance_values[i]

    watt = int(150 + 0.3*hr + 0.2*duration + 0.5*perf + random.randint(-3,3))
    watt_values.append(watt)
    trainings.append({"hr": hr, "duration": duration, "watt": watt})

# ----------------------------
# 4️⃣ Features für ML
# ----------------------------
X = np.array([[t["hr"], t["duration"], fitness_scaled[i], fatigue_scaled[i]] 
              for i, t in enumerate(trainings)])
y = np.array([t["watt"] for t in trainings])

# ----------------------------
# 5️⃣ Modell trainieren
# ----------------------------
model = LinearRegression()
model.fit(X, y)

# ----------------------------
# 6️⃣ Vorhersage heutiges Training
# ----------------------------
hr_today = 160
duration_today = 60

# Fitness/Fatigue für heute berechnen (letzter Stand + heutiger Load)
load_today = 0.5*hr_today + 0.3*duration_today
fitness_today = fitness * 0.95 + load_today * 0.05
fatigue_today = fatigue * 0.8 + load_today * 0.2

# gleiche Skalierung wie beim Training
fitness_today_scaled = fitness_today / fitness_max * 10
fatigue_today_scaled = fatigue_today / fatigue_max * 10
performance_today = fitness_today_scaled - fatigue_today_scaled

predicted = model.predict([[hr_today, duration_today, fitness_today_scaled, fatigue_today_scaled]])[0]

# Simulierter tatsächlicher Wattwert
watt_today = int(150 + 0.3*hr_today + 0.2*duration_today + 0.5*performance_today + random.randint(-3,3))
improvement = (watt_today - predicted) / predicted * 100

# Kommentar
if improvement > 3:
    comment = "Top Training! Du liegst über deiner erwarteten Leistung."
elif improvement < -3:
    comment = "Achtung: Unter der erwarteten Leistung, evtl. Ermüdung."
else:
    comment = "Leistung im Normalbereich."

# ----------------------------
# 7️⃣ Ausgabe
# ----------------------------
print("Heutige Vorhersage (Watt):", round(predicted,1))
print("Tatsächliche Watt:", watt_today)
print("Verbesserung:", round(improvement,1), "%")
print("Kommentar:", comment)
print("Modell-Koeffizienten:", model.coef_)
print("R² Score:", round(model.score(X, y),3))

# ----------------------------
# 8️⃣ Grafische Darstellung
# ----------------------------
plt.figure(figsize=(12,5))
plt.plot(watt_values, label="Watt historisch")
plt.plot(fitness_scaled, label="Fitness (skaliert)")
plt.plot(fatigue_scaled, label="Fatigue (skaliert)")
plt.plot(performance_values, label="Performance (F-F)")
plt.axhline(y=predicted, color='r', linestyle='--', label='Vorhersage heutiges Training')
plt.xlabel("Trainingseinheit")
plt.ylabel("Watt / skaliert")
plt.title("Fitness-Fatigue Verlauf & Watt-Vorhersage")
plt.legend()
plt.show()