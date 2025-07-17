"""
Library management models.

This module defines the database models related to library management.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, DateTime, Boolean, Enum as SQLAEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class BookStatus(str, Enum):
    """Enumeration for book status."""
    AVAILABLE = "available"
    ISSUED = "issued"
    LOST = "lost"
    DAMAGED = "damaged"
    UNDER_REPAIR = "under_repair"
    RESERVED = "reserved"


class Book(Base):
    """Model representing a book in the library."""
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    isbn = Column(String(20), unique=True, index=True)
    publisher = Column(String(255))
    publication_year = Column(Integer)
    edition = Column(String(50))
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("book_categories.id"))
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    shelf_location = Column(String(50))
    added_date = Column(Date, default=date.today)
    status = Column(SQLAEnum(BookStatus), default=BookStatus.AVAILABLE)
    
    # Relationships
    category = relationship("BookCategory", back_populates="books")
    issues = relationship("BookIssue", back_populates="book")
    reservations = relationship("BookReservation", back_populates="book")


class BookCategory(Base):
    """Model representing a book category."""
    __tablename__ = "book_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Relationships
    books = relationship("Book", back_populates="category")


class BookIssue(Base):
    """Model representing a book issue to a student or staff."""
    __tablename__ = "book_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    issue_date = Column(Date, default=date.today, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)
    returned = Column(Boolean, default=False)
    fine_amount = Column(Integer, default=0)  # Fine in smallest currency unit
    remarks = Column(Text)
    
    # Relationships
    book = relationship("Book", back_populates="issues")
    user = relationship("User")


class BookReservation(Base):
    """Model representing a book reservation."""
    __tablename__ = "book_reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reservation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expiry_date = Column(Date, nullable=False)
    status = Column(String(20), default="active")  # active, fulfilled, expired
    
    # Relationships
    book = relationship("Book", back_populates="reservations")
    user = relationship("User")


class LibrarySettings(Base):
    """Model representing library settings."""
    __tablename__ = "library_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    max_books_per_student = Column(Integer, default=2)
    max_books_per_staff = Column(Integer, default=5)
    loan_period_students = Column(Integer, default=14)  # Days
    loan_period_staff = Column(Integer, default=30)  # Days
    fine_per_day = Column(Integer, default=10)  # Fine in smallest currency unit
    reservation_period = Column(Integer, default=3)  # Days
    allow_renewals = Column(Boolean, default=True)
    max_renewals = Column(Integer, default=1) 