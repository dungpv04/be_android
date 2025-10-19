#!/usr/bin/env python3
"""
Script to remove all authentication dependencies from endpoint files.
"""

import os
import re
from pathlib import Path

def remove_auth_dependencies(file_path):
    """Remove auth dependencies from a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove import lines
    content = re.sub(r'from app\.core\.dependencies import.*\n', '', content)
    content = re.sub(r'from app\.core\.auth_db import.*\n', '', content)
    
    # Remove auth parameters from function signatures
    # Pattern to match auth parameters in function signatures
    patterns = [
        r',?\s*current_user:\s*dict\s*=\s*Depends\(get_current_user\),?\s*',
        r',?\s*teacher_user:\s*dict\s*=\s*Depends\(get_teacher_user\),?\s*',
        r',?\s*student_user:\s*dict\s*=\s*Depends\(get_student_user\),?\s*',
        r',?\s*admin_user:\s*Dict\[str,\s*Any\]\s*=\s*Depends\(get_admin_user.*?\),?\s*',
        r',?\s*current_user:\s*dict\s*=\s*Depends\(get_teacher_user\)\s*#.*?\n',
    ]
    
    for pattern in patterns:
        content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
    
    # Clean up trailing commas in function signatures
    content = re.sub(r',\s*\n\s*\):', '\n):', content)
    content = re.sub(r',\s*,', ',', content)  # Remove double commas
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Cleaned auth dependencies from {file_path}")

def main():
    """Main function to process all endpoint files."""
    endpoints_dir = Path("app/api/endpoints")
    
    # Process all Python files in endpoints directory
    for py_file in endpoints_dir.glob("*.py"):
        if py_file.name not in ["__init__.py", "auth.py", "health.py"]:  # Skip these files
            remove_auth_dependencies(py_file)
    
    print("🎉 All authentication dependencies removed!")

if __name__ == "__main__":
    main()
