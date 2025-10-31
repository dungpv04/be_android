from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.core.database import get_supabase
from app.core.auth import auth_service
from app.schemas import AdminCreate, BaseResponse
from app.services import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/create", response_model=BaseResponse)
async def create_admin(
    admin_data: AdminCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new admin user."""
    try:
        # Create auth user with admin role
        auth_user = await auth_service.create_user_with_supabase(
            admin_data.email, 
            admin_data.password,
            user_metadata={"user_type": "admin"}
        )
        
        if not auth_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create admin auth user"
            )
        
        # Create admin profile
        admin_service = AdminService(supabase)
        admin_profile_data = {
            "auth_id": auth_user.id
        }
        
        admin_profile = await admin_service.create(admin_profile_data)
        
        if not admin_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create admin profile"
            )
        
        return BaseResponse(
            message="Admin created successfully",
            data={
                "id": admin_profile.id,
                "email": admin_data.email,
                "user_type": "admin"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create admin error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
