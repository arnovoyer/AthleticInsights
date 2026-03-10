import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    ai_provider: str
    gemini_api_key: str



def load_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./triathlon_data.db"),
        ai_provider=os.getenv("AI_PROVIDER", "mock"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
    )
