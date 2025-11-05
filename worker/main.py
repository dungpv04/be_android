#!/usr/bin/env python3
"""
Hatchet Worker for Student Attendance Management
Handles scheduled background tasks for closing teaching sessions.
"""
import os
import asyncio
from datetime import datetime
from hatchet_sdk import Hatchet
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Hatchet client
hatchet = Hatchet(debug=True)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class CloseSessionInput(BaseModel):
    """Input model for close session task."""
    session_id: int
    scheduled_close_time: str  # ISO format datetime string

# Define the workflow
close_session_workflow = hatchet.workflow(name="close-session-workflow")

@close_session_workflow.task()
async def close_teaching_session(input: CloseSessionInput, context) -> dict:
    """
    Task to close a teaching session by updating its status to 'Closed'.
    This task is scheduled to run at the session's end time.
    """
    try:
        logger.info(f"Starting close session task for session ID: {input.session_id}")
        
        # Update the session status to 'Closed'
        response = supabase.table("teaching_sessions").update({
            "status": "Closed",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", input.session_id).execute()
        
        if response.data:
            logger.info(f"Successfully closed session {input.session_id}")
            return {
                "success": True,
                "session_id": input.session_id,
                "closed_at": datetime.utcnow().isoformat(),
                "message": f"Session {input.session_id} has been closed"
            }
        else:
            logger.error(f"Failed to close session {input.session_id} - no data returned")
            return {
                "success": False,
                "session_id": input.session_id,
                "error": "Failed to update session status"
            }
            
    except Exception as e:
        logger.error(f"Error closing session {input.session_id}: {str(e)}")
        raise Exception(f"Failed to close session {input.session_id}: {str(e)}")

def main():
    """Start the Hatchet worker."""
    logger.info("Starting Hatchet worker for session management...")
    
    # Create the worker
    worker = hatchet.worker("session-worker", workflows=[close_session_workflow])
        
    logger.info("Worker created and workflow registered. Starting worker...")
    worker.start()

if __name__ == "__main__":
    main()
