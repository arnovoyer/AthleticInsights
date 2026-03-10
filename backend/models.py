from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

SportType = Literal["Rad", "Lauf", "Schwimmen"]


class ActivityCreate(BaseModel):
    date: date
    sport: SportType
    duration: int = Field(..., ge=1, le=1440)
    avg_hr: int = Field(..., ge=40, le=230)
    tss: Optional[float] = Field(default=None, ge=0)
    source: str = Field(default="manual", min_length=1)


class ActivityRead(BaseModel):
    id: int
    date: date
    sport: SportType
    duration: int
    avg_hr: int
    tss: float
    source: str


class MetricsRead(BaseModel):
    ctl: float
    atl: float
    tsb: float
    tss_today: float


class InsightRead(BaseModel):
    message: str
