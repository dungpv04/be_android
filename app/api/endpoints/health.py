"""
Health check and system status endpoints.
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Attendance Management API",
        "version": "2.0.0"
    }


@router.get("/status")
async def detailed_status():
    """Detailed system status."""
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "healthy",
            "supabase": "connected"
        },
        "uptime": "running"
    }
