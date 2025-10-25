"""Core module initialization."""

from .config import settings
from .database import get_supabase, get_supabase_admin, supabase_client
from .auth import auth_service

__all__ = ["settings", "get_supabase", "get_supabase_admin", "supabase_client", "auth_service"]
