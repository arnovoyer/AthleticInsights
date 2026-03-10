from fastapi import APIRouter, Depends

from backend.models import ActivityCreate, ActivityRead, InsightRead, MetricsRead
from backend.services.insights import InsightService
from backend.services.metrics import MetricsService

router = APIRouter(prefix="/api", tags=["athlete"])


def get_services():
    from backend.main import get_repository

    return {
        "repo": get_repository(),
        "metrics": MetricsService(),
        "insights": InsightService(),
    }


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/activities", response_model=ActivityRead)
def create_activity(payload: ActivityCreate, services=Depends(get_services)) -> ActivityRead:
    tss = payload.tss
    if tss is None:
        tss = services["metrics"].estimate_tss(payload.duration, payload.avg_hr)

    data = services["repo"].create_activity(payload, tss)
    return ActivityRead(**data)


@router.get("/activities", response_model=list[ActivityRead])
def list_activities(services=Depends(get_services)) -> list[ActivityRead]:
    data = services["repo"].list_activities()
    return [ActivityRead(**row) for row in data]


@router.get("/metrics", response_model=MetricsRead)
def get_metrics(services=Depends(get_services)) -> MetricsRead:
    data = services["repo"].list_activities()
    metrics = services["metrics"].calculate_ctl_atl_tsb(data)
    return MetricsRead(**metrics)


@router.get("/insight", response_model=InsightRead)
def get_insight(services=Depends(get_services)) -> InsightRead:
    data = services["repo"].list_activities()
    metrics = services["metrics"].calculate_ctl_atl_tsb(data)
    last_activity = data[-1] if data else None
    message = services["insights"].generate_insight(last_activity, metrics)
    return InsightRead(message=message)
