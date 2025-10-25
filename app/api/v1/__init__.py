from fastapi import APIRouter
from .auth import router as auth_router
from .academic import router as academic_router
from .users import router as users_router
from .classes import router as classes_router

# Create the main v1 router
v1_router = APIRouter(prefix="/v1")

# Include all sub-routers
v1_router.include_router(auth_router)
v1_router.include_router(academic_router)
v1_router.include_router(users_router)
v1_router.include_router(classes_router)
