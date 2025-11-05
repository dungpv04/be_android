#!/usr/bin/env python3
"""
Test script for Hatchet worker functionality
"""
import os
import sys
import asyncio
from datetime import datetime, timedelta

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worker.main import close_teaching_session


async def test_schedule_session_closure():
    """Test scheduling a session closure."""
    try:
        print("Testing session closure scheduling...")
        
        # Test data
        test_session_id = 1
        test_close_time = datetime.now() + timedelta(minutes=1)  # Schedule for 1 minute from now
        
        print(f"Scheduling closure for session {test_session_id} at {test_close_time}")
        
        # Schedule the task
        scheduled_run = await close_teaching_session.schedule(
            input={
                "session_id": test_session_id,
                "scheduled_close_time": test_close_time.isoformat()
            },
            scheduled_time=test_close_time
        )
        
        print(f"Scheduled run: {scheduled_run}")
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_schedule_session_closure())
