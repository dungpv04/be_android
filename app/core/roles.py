"""
User roles enumeration for role-based access control.
"""
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    
    @classmethod
    def get_all_roles(cls):
        """Get all available roles."""
        return [role.value for role in cls]
    
    @classmethod
    def is_valid_role(cls, role: str) -> bool:
        """Check if role is valid."""
        return role in cls.get_all_roles()
    
    def __str__(self):
        return self.value
