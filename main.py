from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API routers
from app.api.endpoints import auth, health, admin
from app.api.endpoints.subjects import router as subjects_router
from app.api.endpoints.class_students import router as class_students_router
from app.api.endpoints.face_templates import router as face_templates_router
from app.api.endpoints.teaching_sessions import router as teaching_sessions_router
from app.api.endpoints.majors import router as majors_router
from app.api.endpoints.cohorts import router as cohorts_router
from app.api.endpoints.classes import router as classes_router

app = FastAPI(
    title="Attendance Management System API",
    description="A comprehensive API for managing student attendance with Supabase and face recognition",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(admin.router)
app.include_router(subjects_router)  # Add this line
app.include_router(class_students_router)
app.include_router(face_templates_router)
app.include_router(teaching_sessions_router)
app.include_router(majors_router)
app.include_router(cohorts_router)
app.include_router(classes_router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        # Check Supabase connectivity instead of creating database tables
        from app.services.supabase import SupabaseService
        supabase_service = SupabaseService()
        if supabase_service.is_configured():
            print("✅ Supabase service configured successfully")
        else:
            print("⚠️  Supabase service not configured")
    except Exception as e:
        print(f"⚠️  Application startup warning: {e}")
        print("📝 App will start without full connectivity")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Attendance Management System API",
        "version": "2.0.0",
        "status": "Running with Supabase",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
