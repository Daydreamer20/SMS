"""
Re-export dependencies for API v1.
"""

from app.core.database import get_db
from app.core.deps import (
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    get_current_admin,
    get_current_teacher,
    get_current_student,
    check_roles,
)

__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "get_current_active_superuser",
    "get_current_admin",
    "get_current_teacher",
    "get_current_student",
    "check_roles",
] 