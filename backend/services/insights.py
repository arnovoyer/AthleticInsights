class InsightService:
    @staticmethod
    def generate_insight(last_activity: dict | None, metrics: dict[str, float]) -> str:
        if last_activity is None:
            return "Noch keine Einheiten vorhanden. Starte mit einer lockeren Session, um eine Basislinie aufzubauen."

        tsb = metrics["tsb"]
        sport = last_activity["sport"]
        duration = last_activity["duration"]

        if tsb < -20:
            recommendation = "Morgen Ruhetag oder sehr locker, Fokus auf Schlaf und Kohlenhydrate."
        elif tsb < -10:
            recommendation = "Belastung hoch, reduziere Intensitaet und setze auf aktive Regeneration."
        elif tsb < 5:
            recommendation = "Du bist im produktiven Bereich, eine kontrollierte Qualitaetseinheit ist sinnvoll."
        else:
            recommendation = "Du bist frisch, ideal fuer ein Intervall- oder Schwellentraining."

        return (
            f"Starke {sport}-Einheit ueber {duration} Minuten. "
            f"Dein aktueller TSB liegt bei {tsb:.1f}. "
            f"{recommendation}"
        )
