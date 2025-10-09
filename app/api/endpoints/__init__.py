"""
API endpoints package.
"""

# Import router objects directly
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.health import router as health_router
from app.api.endpoints.admin import router as admin_router

__all__ = ["auth_router", "health_router", "admin_router"]
