"""
Pydantic schemas for settings models.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl


class SchoolSettingsBase(BaseModel):
    """Base schema for SchoolSettings model."""
    
    school_name: str
    school_address: str
    school_email: EmailStr
    school_phone: str
    school_website: Optional[HttpUrl] = None
    school_logo: Optional[str] = None
    principal_name: str
    established_date: Optional[datetime] = None
    current_academic_year_id: Optional[int] = None


class SchoolSettingsCreate(SchoolSettingsBase):
    """Schema for creating SchoolSettings."""
    
    pass


class SchoolSettingsUpdate(BaseModel):
    """Schema for updating SchoolSettings."""
    
    school_name: Optional[str] = None
    school_address: Optional[str] = None
    school_email: Optional[EmailStr] = None
    school_phone: Optional[str] = None
    school_website: Optional[HttpUrl] = None
    school_logo: Optional[str] = None
    principal_name: Optional[str] = None
    established_date: Optional[datetime] = None
    current_academic_year_id: Optional[int] = None


class SchoolSettingsInDBBase(SchoolSettingsBase):
    """Base schema for SchoolSettings with DB fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class SchoolSettings(SchoolSettingsInDBBase):
    """Schema for SchoolSettings response."""
    
    pass


class SystemSettingsBase(BaseModel):
    """Base schema for SystemSettings model."""
    
    key: str
    value: str
    value_type: str = "string"  # string, number, boolean, json
    description: Optional[str] = None
    is_public: bool = False


class SystemSettingsCreate(SystemSettingsBase):
    """Schema for creating SystemSettings."""
    
    pass


class SystemSettingsUpdate(BaseModel):
    """Schema for updating SystemSettings."""
    
    value: str
    value_type: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class SystemSettingsInDBBase(SystemSettingsBase):
    """Base schema for SystemSettings with DB fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class SystemSettings(SystemSettingsInDBBase):
    """Schema for SystemSettings response."""
    
    pass


class GradingSystemBase(BaseModel):
    """Base schema for GradingSystem model."""
    
    name: str
    description: Optional[str] = None
    grading_rules: Dict[str, Any]
    is_active: bool = False


class GradingSystemCreate(GradingSystemBase):
    """Schema for creating GradingSystem."""
    
    pass


class GradingSystemUpdate(BaseModel):
    """Schema for updating GradingSystem."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    grading_rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class GradingSystemInDBBase(GradingSystemBase):
    """Base schema for GradingSystem with DB fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class GradingSystem(GradingSystemInDBBase):
    """Schema for GradingSystem response."""
    
    pass 