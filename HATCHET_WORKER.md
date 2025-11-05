# Hatchet Worker for Teaching Session Management

This document explains how the Hatchet worker is integrated into the Student Attendance Management System for automatically closing teaching sessions.

## Overview

The system uses [Hatchet](https://hatchet.run/) to schedule background tasks that automatically close teaching sessions when their end time is reached. This ensures that sessions don't remain open indefinitely and maintains data consistency.

## Architecture

### Components

1. **Main FastAPI Application** (`main.py`)
   - Handles API requests
   - Creates teaching sessions
   - Schedules closure tasks via Hatchet

2. **Hatchet Worker** (`worker/main.py`)
   - Runs as a separate process
   - Executes scheduled session closure tasks
   - Updates session status to "Closed"

3. **Scheduler Service** (`app/core/scheduler.py`)
   - Provides utilities for scheduling and cancelling tasks
   - Integrates with the main application

## Workflow

1. **Session Creation**:
   - User creates a teaching session via API
   - System automatically schedules a closure task for the session's end time
   - Scheduled task ID is stored in the session record

2. **Automatic Closure**:
   - Hatchet executes the scheduled task at the specified time
   - Worker updates the session status to "Closed"
   - Task completion is logged

3. **Manual Operations**:
   - If a session is deleted, the scheduled task is automatically cancelled
   - Sessions can be manually closed via API

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Hatchet Configuration
HATCHET_CLIENT_TOKEN=your_hatchet_token_here

# Supabase Configuration (required for worker)
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_role_key
```

### Docker Compose

The `docker-compose.yml` includes both the main application and the worker:

```yaml
services:
  app:
    # Main FastAPI application
    
  worker:
    # Hatchet worker for background tasks
    command: ["uv", "run", "python", "worker/main.py"]
```

## Usage

### Development

1. **Start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Start manually**:
   ```bash
   # Terminal 1: Start the main application
   uv run python main.py
   
   # Terminal 2: Start the worker
   uv run python worker/main.py
   ```

### Testing

Test the worker functionality:

```bash
uv run python test_worker.py
```

## API Integration

### Database Schema

The `teaching_sessions` table includes a new field:

```sql
ALTER TABLE teaching_sessions 
ADD COLUMN scheduled_task_id VARCHAR(255);
```

### API Changes

Teaching session creation now:
- Automatically schedules closure tasks
- Returns `scheduled_task_id` in responses
- Handles scheduling failures gracefully

Example response:
```json
{
  "id": 1,
  "class_id": 1,
  "session_date": "2024-01-15",
  "start_time": "08:00:00",
  "end_time": "09:30:00",
  "status": "Open",
  "scheduled_task_id": "hatchet_task_123456",
  "created_at": "2024-01-15T07:00:00Z",
  "updated_at": "2024-01-15T07:00:00Z"
}
```

## Monitoring

### Logs

Worker logs provide information about:
- Task execution
- Session closure operations
- Error handling

### Hatchet Dashboard

Monitor scheduled tasks and executions via the Hatchet dashboard at your configured endpoint.

## Error Handling

The system includes robust error handling:

1. **Scheduling Failures**: Sessions are created even if scheduling fails
2. **Worker Failures**: Tasks are retried automatically
3. **Database Errors**: Proper logging and error responses
4. **Cancellation Errors**: Non-blocking warnings for cleanup operations

## Security

- Worker uses Supabase service role key for database operations
- Hatchet client token should be kept secure
- All environment variables should be properly configured

## Troubleshooting

### Common Issues

1. **Worker not starting**:
   - Check `HATCHET_CLIENT_TOKEN` is set
   - Verify Supabase configuration
   - Check network connectivity

2. **Tasks not executing**:
   - Ensure worker is running
   - Check Hatchet dashboard for task status
   - Verify scheduled times are in the future

3. **Database connection errors**:
   - Verify `SUPABASE_SERVICE_KEY` has proper permissions
   - Check database connectivity

### Debug Mode

Enable debug mode by setting `debug=True` in Hatchet client initialization.

## Future Enhancements

Potential improvements:
- Email notifications when sessions are auto-closed
- Analytics on session closure patterns
- Configurable closure warnings before actual closure
- Integration with calendar systems
