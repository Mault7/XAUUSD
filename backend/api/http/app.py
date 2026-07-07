from fastapi import FastAPI

from backend.api.http.routes.alerts import router as alerts_router
from backend.api.http.routes.dashboard import router as dashboard_router
from backend.api.http.routes.health import router as health_router
from backend.api.http.routes.indicators import router as indicators_router
from backend.api.http.routes.market import router as market_router
from backend.api.http.routes.risk import router as risk_router
from backend.api.http.routes.scoring import router as scoring_router
from backend.api.http.routes.structure import router as structure_router
from backend.infrastructure.config.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.include_router(health_router)
    app.include_router(alerts_router)
    app.include_router(dashboard_router)
    app.include_router(market_router)
    app.include_router(indicators_router)
    app.include_router(structure_router)
    app.include_router(risk_router)
    app.include_router(scoring_router)
    return app
