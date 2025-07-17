"""
Pydantic schemas for staff-related models.
"""

from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.staff import StaffType

if TYPE_CHECKING:
    from app.schemas.user import User
    from app.schemas.academic import Class, Subject


class StaffBase(BaseModel):
    """Base schema for Staff model."""
    
    staff_id: str
    staff_type: str = StaffType.TEACHER.value
    department: Optional[str] = None
    designation: Optional[str] = None
    qualification: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_joining: date = Field(default_factory=date.today)
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True


class StaffCreate(StaffBase):
    """Schema for creating a new Staff member."""
    
    user_id: int


class StaffUpdate(BaseModel):
    """Schema for updating a Staff member."""
    
    staff_id: Optional[str] = None
    staff_type: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    qualification: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_joining: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class StaffInDBBase(StaffBase):
    """Base schema for Staff with DB fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class Staff(StaffInDBBase):
    """Schema for Staff response."""
    
    pass


class StaffWithUser(Staff):
    """Staff schema with user information."""
    
    from app.schemas.user import User
    
    user: "User"


class StaffWithClasses(Staff):
    """Staff schema with classes information."""
    
    classes: List["Class"] = []
    subjects: List["Subject"] = [] 