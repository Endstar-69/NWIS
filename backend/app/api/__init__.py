from backend.app.api.auth import router as auth_router
from backend.app.api.wells import router as wells_router
from backend.app.api.formations import router as formations_router
from backend.app.api.events import router as events_router
from backend.app.api.documents import router as documents_router
from backend.app.api.search import router as search_router
from backend.app.api.risk import router as risk_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.simulator import router as simulator_router

__all__ = [
    "auth_router",
    "wells_router",
    "formations_router",
    "events_router",
    "documents_router",
    "search_router",
    "risk_router",
    "alerts_router",
    "recommendations_router",
    "analytics_router",
    "simulator_router",
]
