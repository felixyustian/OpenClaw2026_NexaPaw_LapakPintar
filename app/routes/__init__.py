from .health import router as health_router
from .dashboard import router as dashboard_router
from .agents import router as agents_router

__all__ = ["health_router", "dashboard_router", "agents_router"]
