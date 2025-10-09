"""
Core configuration management for the attendance management system.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database settings (optional - only needed for direct PostgreSQL connections)
    database_url: Optional[str] = None
    
    # Supabase settings
    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str
    
    # JWT settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server settings
    app_name: str = "Attendance Management API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # CORS settings
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


class DatabaseConfig:
    """Database configuration and connection management."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._engine = None
        self._session_factory = None
    
    @property
    def database_url(self) -> str:
        return self.settings.database_url
    
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")
    
    def is_postgresql(self) -> bool:
        return self.database_url.startswith("postgresql")


class AuthConfig:
    """Authentication configuration management."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    @property
    def secret_key(self) -> str:
        return self.settings.secret_key
    
    @property
    def algorithm(self) -> str:
        return self.settings.algorithm
    
    @property
    def access_token_expire_minutes(self) -> int:
        return self.settings.access_token_expire_minutes
    
    def is_supabase_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return (
            self.settings.supabase_url and 
            self.settings.supabase_url != "https://your-project.supabase.co" and
            self.settings.supabase_key and 
            self.settings.supabase_key != "your_supabase_anon_key"
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


@lru_cache()
def get_database_config() -> DatabaseConfig:
    """Get cached database configuration."""
    return DatabaseConfig(get_settings())


@lru_cache()
def get_auth_config() -> AuthConfig:
    """Get cached authentication configuration."""
    return AuthConfig(get_settings())


# Export commonly used instances
settings = get_settings()
db_config = get_database_config()
auth_config = get_auth_config()
