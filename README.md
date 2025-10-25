# Student Attendance Management Backend

A FastAPI-based backend system for managing student attendance with QR code scanning, face recognition support, and Supabase authentication.

## Features

- **User Management**: Students, Teachers, and Admin accounts with Supabase Auth
- **Academic Structure**: Faculties, Departments, Majors, Subjects, Classes
- **Class Management**: Teaching sessions with QR code generation
- **Attendance Tracking**: QR code-based and manual attendance marking
- **Face Recognition Support**: Template storage for face-based attendance (future implementation)
- **RESTful API**: Complete CRUD operations for all entities
- **Authentication**: JWT-based authentication with Supabase
- **Pagination**: Built-in pagination for all list endpoints

## Tech Stack

- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: Supabase Auth
- **Package Manager**: UV
- **Validation**: Pydantic v2
- **ORM**: Supabase Client (PostgreSQL)

## Project Structure

```
app/
├── api/                    # API routes
│   └── v1/                # Version 1 endpoints
│       ├── auth.py        # Authentication endpoints
│       ├── academic.py    # Academic structure endpoints
│       ├── users.py       # User management endpoints
│       └── classes.py     # Class and attendance endpoints
├── core/                  # Core application components
│   ├── config.py          # Application settings
│   ├── database.py        # Database connection
│   └── auth.py            # Authentication logic
├── models/                # Pydantic models (database entities)
├── schemas/               # Request/Response schemas
├── repositories/          # Data access layer
├── services/              # Business logic layer
└── __init__.py
```

## Setup Instructions

### Prerequisites

- Python 3.12 or higher
- UV package manager
- Supabase account and project
- PostgreSQL database (provided by Supabase)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd be_android
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   
   Update the `.env` file with your Supabase credentials:
   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_role_key
   
   # Database Configuration
   DATABASE_URL=your_postgresql_connection_string
   
   # JWT Configuration
   SECRET_KEY=your_super_secret_jwt_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Application Configuration
   APP_NAME=Student Attendance Management
   DEBUG=True
   HOST=0.0.0.0
   PORT=8000
   ```

4. **Database Setup**
   
   Run the SQL schema provided in the original README against your Supabase database. You can use the Supabase SQL editor or any PostgreSQL client.

5. **Run the application**
   ```bash
   # Development mode
   uv run python main.py
   
   # Or using uvicorn directly
   uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user info

### Academic Structure
- `GET/POST /api/v1/academic/faculties` - Faculty management
- `GET/POST /api/v1/academic/departments` - Department management
- `GET/POST /api/v1/academic/majors` - Major management
- `GET/POST /api/v1/academic/subjects` - Subject management
- `GET /api/v1/academic/academic-years/current` - Current academic year

### User Management
- `GET/POST /api/v1/users/students` - Student management
- `GET/POST /api/v1/users/teachers` - Teacher management
- `GET /api/v1/users/students/{id}` - Get student by ID
- `GET /api/v1/users/students/code/{code}` - Get student by code

### Classes & Attendance
- `GET/POST /api/v1/classes` - Class management
- `POST /api/v1/classes/{id}/sessions` - Create teaching session
- `POST /api/v1/classes/sessions/{id}/qr-code` - Generate QR code
- `POST /api/v1/classes/sessions/{id}/attendance` - Mark attendance
- `POST /api/v1/classes/sessions/{id}/attendance/qr` - Mark attendance via QR
- `GET /api/v1/classes/{id}/attendance/statistics` - Attendance statistics

## Database Schema

The application uses the following main entities:

- **Academic Structure**: AcademicYears, Semesters, StudyPhases
- **Organization**: Faculties, Departments, Majors, Subjects
- **Users**: Students, Teachers, Admins
- **Classes**: Classes, ClassStudents (enrollment)
- **Sessions**: TeachingSessions with QR codes
- **Attendance**: Attendance records with timestamps
- **Face Recognition**: FaceTemplates for biometric attendance

## Authentication Flow

1. **Registration**: Users register with email/password and user type
2. **Supabase Auth**: Account created in Supabase Auth
3. **Profile Creation**: User profile created in respective table (students/teachers)
4. **Login**: Returns JWT token for subsequent requests
5. **Protected Routes**: Include Bearer token in Authorization header

## QR Code Attendance Flow

1. **Session Creation**: Teacher creates a teaching session
2. **QR Generation**: Generate time-limited QR code for session
3. **Student Scan**: Student scans QR code with mobile app
4. **Validation**: System validates QR code and marks attendance
5. **Tracking**: Attendance recorded with timestamp and metadata

## Development

### Running Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black .
uv run isort .
```

### Linting
```bash
uv run flake8
```

## Deployment

1. **Set Environment Variables**: Configure production environment variables
2. **Database Migration**: Ensure database schema is up to date
3. **CORS Settings**: Update allowed origins for production
4. **Security**: Use strong JWT secret keys and secure database credentials
5. **Monitoring**: Set up logging and monitoring for production

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

This project is licensed under the MIT License.
