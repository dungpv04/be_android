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
        user_metadata: Optional[Dict[str, Any]] = None,
        user_role: str = None,
        profile_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Register a new user with Supabase Auth and create profile record."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        
        try:
            # Use standard Supabase signup
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            
            if not response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account"
                )
            
            auth_user = response.user
            logger.info(f"Successfully created auth user: {auth_user.id}")
            
            # Create profile record in appropriate table based on role
            if user_role and profile_data:
                await self._create_user_profile(auth_user.id, user_role, profile_data)
            
            return {
                "id": auth_user.id,
                "email": auth_user.email,
                "user_metadata": auth_user.user_metadata,
                "created_at": auth_user.created_at
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def _create_user_profile(self, auth_id: str, user_role: str, profile_data: Dict[str, Any]):
        """Create user profile record in the appropriate table using repositories."""
        try:
            from uuid import UUID
            from datetime import datetime
            
            if user_role == "TEACHER":
                from app.repositories.teachers import TeacherRepository
                from app.schemas.users import TeacherCreate
                
                teacher_repo = TeacherRepository()
                
                # Convert birth_date string back to date if it exists
                birth_date = None
                if profile_data.get("birth_date"):
                    birth_date = datetime.fromisoformat(profile_data["birth_date"]).date()
                
                teacher_create_data = TeacherCreate(
                    auth_id=UUID(auth_id),
                    teacher_code=profile_data.get("teacher_code"),
                    full_name=profile_data.get("full_name"),
                    phone=profile_data.get("phone"),
                    birth_date=birth_date
                )
                
                teacher_record = await teacher_repo.create(teacher_create_data)
                logger.info(f"Created teacher profile: {teacher_record}")
                
            elif user_role == "STUDENT":
                from app.repositories.students import StudentRepository
                from app.schemas.users import StudentCreate
                
                student_repo = StudentRepository()
                
                # Convert birth_date string back to date if it exists
                birth_date = None
                if profile_data.get("birth_date"):
                    birth_date = datetime.fromisoformat(profile_data["birth_date"]).date()
                
                student_create_data = StudentCreate(
                    auth_id=UUID(auth_id),
                    student_code=profile_data.get("student_code"),
                    full_name=profile_data.get("full_name"),
                    phone=profile_data.get("phone"),
                    birth_date=birth_date,
                    major_id=profile_data.get("major_id"),
                    cohort_id=profile_data.get("cohort_id"),
                    class_id=profile_data.get("class_id")
                )
                
                student_record = await student_repo.create(student_create_data)
                logger.info(f"Created student profile: {student_record}")
                
            else:
                logger.warning(f"Unknown user role: {user_role}")
                
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            # Don't raise exception here as auth user was already created
            # Could implement cleanup logic here if needed
    
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
