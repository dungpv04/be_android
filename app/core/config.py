from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings using Pydantic Settings."""
    
    # Application
    app_name: str = "Student Attendance Management"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    
    # Database
    database_url: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
