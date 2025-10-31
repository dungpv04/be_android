#!/usr/bin/env python3
"""
Script to add admin record for existing auth user
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import get_supabase_client
from app.services.admin import AdminService

async def add_admin_record():
    """Add admin record for existing auth user"""
    
    # The auth_id from your login response
    auth_id = "20bc9fb9-8fb2-4a57-91ae-8dab0647e411"
    
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Create admin service
        admin_service = AdminService(supabase)
        
        # Check if admin already exists
        existing_admin = await admin_service.get_by_auth_id(auth_id)
        if existing_admin:
            print(f"Admin already exists with ID: {existing_admin.id}")
            return
        
        # Create admin record
        admin_data = {"auth_id": auth_id}
        admin = await admin_service.create(admin_data)
        
        if admin:
            print(f"✅ Admin record created successfully!")
            print(f"Admin ID: {admin.id}")
            print(f"Auth ID: {admin.auth_id}")
        else:
            print("❌ Failed to create admin record")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(add_admin_record())
