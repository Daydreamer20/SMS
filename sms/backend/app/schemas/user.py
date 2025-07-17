"""
Pydantic schemas for user-related models.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RoleBase(BaseModel):
    """Base schema for Role model."""
    
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating a new Role."""
    
    pass


class RoleUpdate(RoleBase):
    """Schema for updating a Role."""
    
    name: Optional[str] = None


class RoleInDBBase(RoleBase):
    """Base schema for Role with DB fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class Role(RoleInDBBase):
    """Schema for Role response."""
    
    pass


class UserBase(BaseModel):
    """Base schema for User model."""
    
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new User."""
    
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a User."""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    """Base schema for User with DB fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class User(UserInDBBase):
    """Schema for User response."""
    
    roles: List[Role] = []


class UserWithPassword(UserInDBBase):
    """Schema for User with hashed password (for internal use only)."""
    
    hashed_password: str


class UserLogin(BaseModel):
    """Schema for user login."""
    
    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token."""
    
    access_token: str
    token_type: str = "bearer"
    expires_at: int  # Unix timestamp
    refresh_token: str


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    
    sub: str  # Subject (user ID)
    exp: int  # Expiration time
    roles: List[str] = [] 