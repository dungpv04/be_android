# Attendance Management System API

A comprehensive FastAPI application for managing student attendance with face recognition capabilities and Supabase authentication.

## Features

- **Authentication**: Supabase-based authentication for students and teachers
- **User Management**: CRUD operations for students and teachers
- **Academic Structure**: Management of majors, subjects, cohorts, and classes
- **Session Management**: Teaching sessions with QR code support
- **Attendance Tracking**: Real-time attendance with face recognition integration
- **Role-based Access**: Different permissions for students and teachers

## Database Schema

The application manages the following entities:

### Core Entities
- **Students**: Student profiles with authentication
- **Teachers**: Teacher profiles with authentication
- **Majors**: Academic departments/fields of study
- **Cohorts**: Student groups by enrollment year
- **Subjects**: Course subjects
- **Classes**: Specific class instances linking subjects and teachers

### Attendance System
- **Teaching Sessions**: Scheduled class sessions with QR codes
- **Attendances**: Attendance records with confidence scores
- **Face Templates**: Face encoding data for recognition
- **Class Students**: Enrollment relationships

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Supabase account
- uv package manager ([install here](https://docs.astral.sh/uv/getting-started/installation/))

## Installation

### Run with Docker

```bash
docker compose up -d --build #first time run
docker compose up -d #After first run
docker compose logs -f #See logs
```
### Run manually

1. **Clone and navigate to the project:**
   ```bash
   cd /home/dungpv04/code/be_android
   ```

2. **Initialize the project with uv:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   
   Or manually:
   ```bash
   uv sync
   ```

3. **Environment Configuration:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your actual values:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Database Setup:**
   - Ensure your PostgreSQL database is running
   - The application will automatically create tables on startup

5. **Start the application:**
   ```bash
   ./start.sh
   ```
   
   Or manually:
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Documentation

Once running, access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user info

### Students
- `GET /students/` - List all students
- `GET /students/{id}` - Get student by ID
- `POST /students/` - Create student (teacher only)
- `PUT /students/{id}` - Update student
- `DELETE /students/{id}` - Delete student (teacher only)
- `GET /students/class/{class_id}` - Get students by class

### Teachers
- `GET /teachers/` - List all teachers
- `GET /teachers/{id}` - Get teacher by ID
- `POST /teachers/` - Create teacher (teacher only)
- `PUT /teachers/{id}` - Update teacher
- `DELETE /teachers/{id}` - Delete teacher

### Classes
- `GET /classes/` - List all classes
- `GET /classes/{id}` - Get class by ID
- `POST /classes/` - Create class (teacher only)
- `PUT /classes/{id}` - Update class (teacher only)
- `DELETE /classes/{id}` - Delete class (teacher only)
- `GET /classes/teacher/{teacher_id}` - Get classes by teacher

### Teaching Sessions
- `GET /sessions/` - List all sessions
- `GET /sessions/{id}` - Get session by ID
- `POST /sessions/` - Create session (teacher only)
- `PUT /sessions/{id}` - Update session (teacher only)
- `DELETE /sessions/{id}` - Delete session (teacher only)
- `GET /sessions/class/{class_id}` - Get sessions by class

### Attendance
- `GET /attendances/` - List all attendances (teacher only)
- `GET /attendances/{id}` - Get attendance by ID
- `POST /attendances/` - Create attendance
- `PUT /attendances/{id}` - Update attendance (teacher only)
- `DELETE /attendances/{id}` - Delete attendance (teacher only)
- `GET /attendances/session/{session_id}` - Get attendances by session
- `GET /attendances/student/{student_id}` - Get attendances by student

### Academic Structure
- `GET /majors/` - List all majors
- `GET /subjects/` - List all subjects
- Plus full CRUD operations for both (teacher only for create/update/delete)

## Authentication Flow

1. **Registration**: Users register with email/password and user type (student/teacher)
2. **Profile Creation**: Additional profile information is stored in the respective tables
3. **Login**: Returns JWT token with user type and ID
4. **Authorization**: Endpoints check user roles and permissions

## Security Features

- JWT-based authentication
- Role-based access control
- Supabase integration for secure user management
- Password hashing with bcrypt
- CORS configuration for web app integration

## Database Integration

- SQLAlchemy ORM for database operations
- PostgreSQL with psycopg2 driver
- Automatic table creation
- Foreign key relationships maintained
- JSON support for face encoding data

## Development

### Project Structure
```
be_android/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic models for API
├── crud.py              # Database CRUD operations
├── auth.py              # Authentication and authorization
├── utils.py             # Helper utilities
├── routers/             # API route handlers
│   ├── auth.py
│   ├── students.py
│   ├── teachers.py
│   ├── classes.py
│   ├── sessions.py
│   ├── attendances.py
│   ├── majors.py
│   └── subjects.py
├── pyproject.toml       # Project configuration and dependencies
├── uv.lock              # Locked dependencies (auto-generated)
├── .env.example         # Environment variables template
├── setup.sh             # Project initialization script
├── start.sh             # Startup script
└── test_api.py          # API testing script
```

### Package Management with uv

```bash
# Add a new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Remove a dependency
uv remove package-name

# Update dependencies
uv sync

# Run commands in the virtual environment
uv run python script.py
uv run uvicorn main:app --reload

# Install from lock file (production)
uv sync --frozen
```

### Adding New Features

1. **Models**: Add new SQLAlchemy models in `models.py`
2. **Schemas**: Define Pydantic schemas in `schemas.py`
3. **CRUD**: Implement database operations in `crud.py`
4. **Routes**: Create API endpoints in `routers/`
5. **Auth**: Add authorization logic as needed

## Production Deployment

For production deployment:

1. **Environment**: Set proper environment variables
2. **CORS**: Configure allowed origins
3. **Database**: Use production PostgreSQL instance
4. **HTTPS**: Enable SSL/TLS
5. **Monitoring**: Add logging and monitoring
6. **Scaling**: Consider using Gunicorn or similar WSGI server

## Face Recognition Integration

The system includes `face_templates` table for storing face encodings. To integrate face recognition:

1. **Image Upload**: Add endpoints for uploading student photos
2. **Face Encoding**: Process images to extract face encodings
3. **Attendance**: Match faces during attendance marking
4. **Confidence Scoring**: Store confidence scores for accuracy tracking
