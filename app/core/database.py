from supabase import create_client, Client
from app.core.config import settings


class SupabaseClient:
    """Supabase client singleton."""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
    
    @property
    def client(self) -> Client:
        return self._client
    
    def get_service_client(self) -> Client:
        """Get Supabase client with service key for admin operations."""
        return create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )


# Global instance
supabase_client = SupabaseClient()


def get_supabase() -> Client:
    """Dependency to get Supabase client."""
    return supabase_client.client


def get_supabase_admin() -> Client:
    """Dependency to get Supabase admin client."""
    return supabase_client.get_service_client()
