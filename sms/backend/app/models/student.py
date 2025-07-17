"""
Student model definitions.
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import User

if TYPE_CHECKING:
    from app.models.academic import Class, Grade


class Gender(str, Enum):
    """Enumeration for gender types."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    NOT_SPECIFIED = "not_specified"


class BloodGroup(str, Enum):
    """Enumeration for blood groups."""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    NOT_KNOWN = "Not Known"


class Student(Base):
    """Student model for student information."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    admission_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    roll_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(20), default=Gender.NOT_SPECIFIED.value)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default=BloodGroup.NOT_KNOWN.value)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    admission_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key relationships
    class_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    user: Mapped[User] = relationship("User", backref="student")
    class_: Mapped[Optional["Class"]] = relationship("Class", back_populates="students")
    parent_guardian: Mapped[Optional["ParentGuardian"]] = relationship("ParentGuardian", back_populates="students")
    grades: Mapped[List["Grade"]] = relationship("Grade", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of Student."""
        return f"<Student {self.admission_number}>"


# Association table for parent-student relationship
parent_student = Table(
    "parent_student",
    Base.metadata,
    Column("parent_id", Integer, ForeignKey("parent_guardians.id", ondelete="CASCADE"), primary_key=True),
    Column("student_id", Integer, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
)


class ParentGuardian(Base):
    """Parent or Guardian model."""

    __tablename__ = "parent_guardians"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    relationship_type: Mapped[str] = mapped_column(String(50))  # father, mother, guardian, etc.
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped[Optional[User]] = relationship("User", backref="parent_guardian")
    students: Mapped[List[Student]] = relationship(Student, secondary=parent_student, back_populates="parent_guardian")
    
    def __repr__(self) -> str:
        """String representation of ParentGuardian."""
        return f"<ParentGuardian {self.first_name} {self.last_name}>" 