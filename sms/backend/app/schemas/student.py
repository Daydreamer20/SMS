"""
Pydantic schemas for student-related models.
"""

from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.student import Gender, BloodGroup

if TYPE_CHECKING:
    from app.schemas.academic import Class
    from app.schemas.user import User


class ParentGuardianBase(BaseModel):
    """Base schema for ParentGuardian model."""
    
    first_name: str
    last_name: str
    relationship_type: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None


class ParentGuardianCreate(ParentGuardianBase):
    """Schema for creating a new ParentGuardian."""
    
    pass


class ParentGuardianUpdate(BaseModel):
    """Schema for updating a ParentGuardian."""
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    relationship_type: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    occupation: Optional[str] = None


class ParentGuardianInDBBase(ParentGuardianBase):
    """Base schema for ParentGuardian with DB fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ParentGuardian(ParentGuardianInDBBase):
    """Schema for ParentGuardian response."""
    
    pass


class StudentBase(BaseModel):
    """Base schema for Student model."""
    
    admission_number: str
    roll_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: str = Gender.NOT_SPECIFIED.value
    blood_group: Optional[str] = BloodGroup.NOT_KNOWN.value
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    admission_date: date = Field(default_factory=date.today)
    class_id: Optional[int] = None


class StudentCreate(StudentBase):
    """Schema for creating a new Student."""
    
    user_id: int


class StudentUpdate(BaseModel):
    """Schema for updating a Student."""
    
    admission_number: Optional[str] = None
    roll_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    admission_date: Optional[date] = None
    class_id: Optional[int] = None


class StudentInDBBase(StudentBase):
    """Base schema for Student with DB fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class Student(StudentInDBBase):
    """Schema for Student response."""
    
    parent_guardian: Optional[ParentGuardian] = None
    

class StudentWithClass(Student):
    """Student schema with class information."""
    
    from app.schemas.academic import Class
    
    class_: Optional["Class"] = None


class StudentWithUser(Student):
    """Student schema with user information."""
    
    from app.schemas.user import User
    
    user: "User" 