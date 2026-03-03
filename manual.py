max_hr = 204
ftp = 236

duration = 60
hr_avg = 160
watt_avg = 190

intensity = hr_avg / max_hr
load = duration * intensity

trainings = [
    {"hr":150, "watt":180},
    {"hr":160, "watt":185},
    {"hr":170, "watt":200},
    {"hr":180, "watt":210},
]

sum_watt = 0
count = 0

hr_values = []
watt_values =[]

for training in trainings:
    hr_values.append(training["hr"])
    watt_values.append(training["watt"])

mean_hr = sum(hr_values) / len(hr_values)
mean_watt = sum(watt_values)/len(watt_values)

zaehler = 0
nenner = 0

for i in range(len(hr_values)):
    zaehler += (hr_values[i] - mean_hr) * (watt_values[i] - mean_watt)
    nenner += (hr_values[i] - mean_hr) ** 2

a = zaehler / nenner
b = mean_watt - a * mean_hr

predicted_watt = a * hr_avg + b

improvement = (watt_avg - predicted_watt) / predicted_watt * 100

if improvement > 5:
    print("Deutliche Leistungssteigerung bei gleicher Herzfrequenz.")
elif improvement > 0:
    print("Leichte Verbesserung.")
elif improvement > -5:
    print("Leicht unter Erwartung – normale Schwankung.")
else:
    print("Deutlich unter Trend – mögliche Ermüdung.")



for training in trainings:
    if training["hr"] >= 158 and training["hr"] <= 162:
        sum_watt += training["watt"]
        count += 1

if count > 0:
    average_watt = sum_watt / count
    improvement = (watt_avg - average_watt) / average_watt * 100

    print("Durchschnitt damals:", average_watt)
    print("Heutige Verbesserung:", improvement, "%")
else:
    print("Keine Vergleichswerte gefunden")

print("Intensität:", intensity)
print("Load:", load)