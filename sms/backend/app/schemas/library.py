"""
Library management schemas.

This module defines the Pydantic schemas for library management.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, validator, constr, conint

from app.models.library import BookStatus


# BookCategory schemas
class BookCategoryBase(BaseModel):
    """Base schema for book category."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class BookCategoryCreate(BookCategoryBase):
    """Schema for creating a book category."""
    pass


class BookCategoryUpdate(BookCategoryBase):
    """Schema for updating a book category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class BookCategory(BookCategoryBase):
    """Schema for returning a book category."""
    id: int

    class Config:
        orm_mode = True


# Book schemas
class BookBase(BaseModel):
    """Base schema for book."""
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = Field(None, ge=1000, le=date.today().year)
    edition: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    total_copies: int = Field(1, ge=0)
    available_copies: int = Field(1, ge=0)
    shelf_location: Optional[str] = None
    status: BookStatus = BookStatus.AVAILABLE
    
    @validator('isbn')
    def validate_isbn(cls, v):
        """Validate that ISBN is either 10 or 13 digits."""
        if v is not None and not (len(v) == 10 or len(v) == 13):
            raise ValueError('ISBN must be either 10 or 13 digits')
        return v


class BookCreate(BookBase):
    """Schema for creating a book."""
    pass


class BookUpdate(BookBase):
    """Schema for updating a book."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    total_copies: Optional[int] = Field(None, ge=0)
    available_copies: Optional[int] = Field(None, ge=0)
    status: Optional[BookStatus] = None


class Book(BookBase):
    """Schema for returning a book."""
    id: int
    added_date: date
    
    class Config:
        orm_mode = True


class BookWithCategory(Book):
    """Schema for returning a book with its category details."""
    category: Optional[BookCategory] = None


# BookIssue schemas
class BookIssueBase(BaseModel):
    """Base schema for book issue."""
    book_id: int
    user_id: int
    issue_date: date = Field(default_factory=date.today)
    due_date: date
    returned: bool = False
    fine_amount: int = 0
    remarks: Optional[str] = None


class BookIssueCreate(BookIssueBase):
    """Schema for creating a book issue."""
    pass


class BookIssueUpdate(BaseModel):
    """Schema for updating a book issue."""
    return_date: Optional[date] = None
    returned: Optional[bool] = None
    fine_amount: Optional[int] = None
    remarks: Optional[str] = None


class BookIssue(BookIssueBase):
    """Schema for returning a book issue."""
    id: int
    return_date: Optional[date] = None
    
    class Config:
        orm_mode = True


class BookIssueWithDetails(BookIssue):
    """Schema for returning a book issue with book and user details."""
    book: Book
    user_name: str
    user_role: str


# BookReservation schemas
class BookReservationBase(BaseModel):
    """Base schema for book reservation."""
    book_id: int
    user_id: int
    reservation_date: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: date
    status: str = "active"


class BookReservationCreate(BookReservationBase):
    """Schema for creating a book reservation."""
    pass


class BookReservationUpdate(BaseModel):
    """Schema for updating a book reservation."""
    status: Optional[str] = None


class BookReservation(BookReservationBase):
    """Schema for returning a book reservation."""
    id: int
    
    class Config:
        orm_mode = True


class BookReservationWithDetails(BookReservation):
    """Schema for returning a book reservation with book and user details."""
    book: Book
    user_name: str
    user_role: str


# LibrarySettings schemas
class LibrarySettingsBase(BaseModel):
    """Base schema for library settings."""
    max_books_per_student: int = Field(2, ge=1)
    max_books_per_staff: int = Field(5, ge=1)
    loan_period_students: int = Field(14, ge=1)  # Days
    loan_period_staff: int = Field(30, ge=1)  # Days
    fine_per_day: int = Field(10, ge=0)  # Fine in smallest currency unit
    reservation_period: int = Field(3, ge=1)  # Days
    allow_renewals: bool = True
    max_renewals: int = Field(1, ge=0) 