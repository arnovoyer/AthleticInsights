from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.config import load_settings
from backend.db.repository import ActivityRepository

settings = load_settings()
_repo = ActivityRepository(settings.database_url)


app = FastAPI(title="AthleticInsights API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "AthleticInsights Backend läuft"}



def get_repository() -> ActivityRepository:
    return _repo
