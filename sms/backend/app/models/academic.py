"""
Academic models for curriculum, classes, grades and related entities.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Text, Float, Boolean, Date, DateTime, Time, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.staff import Teacher


class Class(Base):
    """Class model representing a school class/grade."""

    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    section: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    academic_year: Mapped[str] = mapped_column(String(20))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key relationships
    teacher_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    teacher: Mapped[Optional["Teacher"]] = relationship("Teacher", back_populates="classes")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="class_")
    
    def __repr__(self) -> str:
        """String representation of Class."""
        return f"<Class {self.name} {self.section or ''}>"


class Subject(Base):
    """Subject model representing academic subjects."""

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    credits: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    grades: Mapped[List["Grade"]] = relationship("Grade", back_populates="subject")
    
    def __repr__(self) -> str:
        """String representation of Subject."""
        return f"<Subject {self.name}>"


class GradeType(str, Enum):
    """Enumeration for grade types."""
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"
    EXAM = "exam"
    PROJECT = "project"
    PARTICIPATION = "participation"
    OTHER = "other"


class Grade(Base):
    """Grade model for student assessment results."""

    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    value: Mapped[float] = mapped_column(Float)
    max_value: Mapped[float] = mapped_column(Float, default=100.0)
    grade_type: Mapped[str] = mapped_column(String(20), default=GradeType.OTHER.value)
    term: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "Term 1", "Semester 1"
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    graded_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key relationships
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    
    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="grades")
    subject: Mapped[Subject] = relationship("Subject", back_populates="grades")
    
    def __repr__(self) -> str:
        """String representation of Grade."""
        return f"<Grade {self.value}/{self.max_value} for {self.student_id} in {self.subject_id}>"


class ExaminationType(str, Enum):
    """Enumeration for examination types."""
    MIDTERM = "midterm"
    FINAL = "final"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    PROJECT = "project"
    OTHER = "other"


class Examination(Base):
    """Examination model for defining examinations."""

    __tablename__ = "examinations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    exam_type: Mapped[str] = mapped_column(String(20), default=ExaminationType.OTHER.value)
    start_date: Mapped[datetime] = mapped_column(Date)
    end_date: Mapped[datetime] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        """String representation of Examination."""
        return f"<Examination {self.name} ({self.exam_type})>"


class StudentPerformanceReport(Base):
    """Model for storing comprehensive student performance reports."""

    __tablename__ = "student_performance_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    term: Mapped[str] = mapped_column(String(50))  # e.g., "Term 1", "Semester 1", "Annual"
    academic_year: Mapped[str] = mapped_column(String(20))
    overall_grade: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    attendance_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    teacher_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    principal_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    areas_for_improvement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key relationships
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    
    # Relationships
    student: Mapped["Student"] = relationship("Student", backref="performance_reports")
    class_: Mapped[Class] = relationship("Class")
    
    def __repr__(self) -> str:
        """String representation of StudentPerformanceReport."""
        return f"<StudentPerformanceReport {self.student_id} - {self.term} {self.academic_year}>" 