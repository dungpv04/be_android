"""
Supabase authentication service.
"""
from supabase import create_client, Client
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import logging

from app.core.config import get_auth_config

logger = logging.getLogger(__name__)


class SupabaseService:
    """Manages Supabase authentication operations."""
    
    def __init__(self):
        self.auth_config = get_auth_config()
        self._supabase_client: Optional[Client] = None
        self._supabase_admin: Optional[Client] = None
        self._initialize_clients()
    
    def _initialize_clients(self) -> bool:
        """Initialize Supabase clients if configuration is valid."""
        try:
            if self.auth_config.is_supabase_configured():
                self._supabase_client = create_client(
                    self.auth_config.settings.supabase_url,
                    self.auth_config.settings.supabase_key
                )
                self._supabase_admin = create_client(
                    self.auth_config.settings.supabase_url,
                    self.auth_config.settings.supabase_service_role_key
                )
                logger.info("Supabase clients initialized successfully")
                return True
            else:
                logger.warning("Supabase configuration not set up. Auth endpoints will not work.")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize Supabase clients: {e}")
            return False
    
    @property
    def client(self) -> Client:
        """Get Supabase client."""
        if not self._supabase_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        return self._supabase_client
    
    @property
    def admin(self) -> Client:
        """Get Supabase admin client."""
        if not self._supabase_admin:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        return self._supabase_admin
    
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return self._supabase_client is not None and self._supabase_admin is not None
    
    async def register_user(
        self, 
        email: str, 
        password: str, 
        user_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Register a new user with Supabase Auth."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        
        try:
            response = self.admin.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": user_metadata or {}
            })
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user"
                )
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with Supabase."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user from Supabase by ID."""
        if not self.is_configured():
            return None
        
        try:
            response = self.admin.auth.admin.get_user_by_id(user_id)
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata
                }
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
        
        return None
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using Supabase."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        
        try:
            response = self.client.auth.refresh_session(refresh_token)
            if response.session:
                return {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "user": response.user
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed"
            )

    # Admin user management methods
    async def admin_create_user(
        self, 
        email: str, 
        password: str, 
        user_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new user as admin."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        
        try:
            response = self.admin.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": user_metadata or {}
            })
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata,
                    "created_at": response.user.created_at
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user"
                )
        except Exception as e:
            logger.error(f"Admin user creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User creation failed: {str(e)}"
            )
    
    async def admin_delete_user(self, user_id: str) -> bool:
        """Delete a user as admin."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        
        try:
            response = self.admin.auth.admin.delete_user(user_id)
            return True
        except Exception as e:
            logger.error(f"Admin user deletion failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User deletion failed: {str(e)}"
            )
    
    async def admin_update_user(
        self, 
        user_id: str, 
        email: Optional[str] = None,
        password: Optional[str] = None,
        user_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update a user as admin."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        
        try:
            update_data = {}
            if email:
                update_data["email"] = email
            if password:
                update_data["password"] = password
            if user_metadata:
                update_data["user_metadata"] = user_metadata
            
            response = self.admin.auth.admin.update_user_by_id(user_id, update_data)
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update user"
                )
        except Exception as e:
            logger.error(f"Admin user update failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User update failed: {str(e)}"
            )
    
    async def admin_list_users(self, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """List all users as admin."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        
        try:
            response = self.admin.auth.admin.list_users(page=page, per_page=per_page)
            
            users = []
            for user in response:
                users.append({
                    "id": user.id,
                    "email": user.email,
                    "user_metadata": user.user_metadata,
                    "created_at": user.created_at,
                    "last_sign_in_at": user.last_sign_in_at
                })
            
            return {
                "users": users,
                "total": len(users)
            }
        except Exception as e:
            logger.error(f"Admin list users failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to list users: {str(e)}"
            )


# Global Supabase service instance
supabase_service = SupabaseService()
