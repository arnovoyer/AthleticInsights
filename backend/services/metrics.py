from datetime import datetime

import pandas as pd


class MetricsService:
    @staticmethod
    def estimate_tss(duration_min: int, avg_hr: int, lthr: int = 170) -> float:
        if lthr <= 0:
            return 0.0
        return float((duration_min * avg_hr * (avg_hr / lthr)) / (lthr * 60) * 100)

    @staticmethod
    def calculate_ctl_atl_tsb(activities: list[dict]) -> dict[str, float]:
        if not activities:
            return {"ctl": 0.0, "atl": 0.0, "tsb": 0.0, "tss_today": 0.0}

        df = pd.DataFrame(activities)
        df["date"] = pd.to_datetime(df["date"])

        idx = pd.date_range(df["date"].min(), datetime.now())
        daily_tss = df.groupby("date")["tss"].sum().reindex(idx, fill_value=0)

        ctl = daily_tss.ewm(span=42, adjust=False).mean()
        atl = daily_tss.ewm(span=7, adjust=False).mean()
        tsb = ctl.shift(1).fillna(0) - atl.shift(1).fillna(0)

        return {
            "ctl": float(ctl.iloc[-1]),
            "atl": float(atl.iloc[-1]),
            "tsb": float(tsb.iloc[-1]),
            "tss_today": float(daily_tss.iloc[-1]),
        }
