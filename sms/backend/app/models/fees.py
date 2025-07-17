"""
Fee management model definitions.
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PaymentMethod(str, Enum):
    """Enumeration for payment methods."""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    CHEQUE = "cheque"
    ONLINE = "online"
    OTHER = "other"


class PaymentStatus(str, Enum):
    """Enumeration for payment status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_PAID = "partially_paid"


class FeeCategory(Base):
    """Fee Category model."""

    __tablename__ = "fee_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    fee_structures: Mapped[List["FeeStructure"]] = relationship("FeeStructure", back_populates="category")
    
    def __repr__(self) -> str:
        """String representation of FeeCategory."""
        return f"<FeeCategory {self.name}>"


class FeeStructure(Base):
    """Fee Structure model."""

    __tablename__ = "fee_structures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    amount: Mapped[float] = mapped_column(Float)
    academic_year: Mapped[str] = mapped_column(String(20))
    term: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_period: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # monthly, quarterly, etc.
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("fee_categories.id", ondelete="CASCADE"))
    class_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    category: Mapped[FeeCategory] = relationship("FeeCategory", back_populates="fee_structures")
    class_ = relationship("Class", backref="fee_structures")
    due_dates: Mapped[List["FeeDueDate"]] = relationship("FeeDueDate", back_populates="fee_structure")
    
    def __repr__(self) -> str:
        """String representation of FeeStructure."""
        return f"<FeeStructure {self.title} {self.amount}>"


class FeeDueDate(Base):
    """Fee Due Date model."""

    __tablename__ = "fee_due_dates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    due_date: Mapped[date] = mapped_column(Date)
    grace_period_days: Mapped[int] = mapped_column(Integer, default=0)
    penalty_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    fee_structure_id: Mapped[int] = mapped_column(Integer, ForeignKey("fee_structures.id", ondelete="CASCADE"))
    
    # Relationships
    fee_structure: Mapped[FeeStructure] = relationship("FeeStructure", back_populates="due_dates")
    
    def __repr__(self) -> str:
        """String representation of FeeDueDate."""
        return f"<FeeDueDate {self.due_date}>"


class FeeTransaction(Base):
    """Fee Transaction model."""

    __tablename__ = "fee_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amount_paid: Mapped[float] = mapped_column(Float)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    payment_method: Mapped[str] = mapped_column(String(50), default=PaymentMethod.CASH.value)
    transaction_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payment_status: Mapped[str] = mapped_column(String(50), default=PaymentStatus.COMPLETED.value)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    fee_structure_id: Mapped[int] = mapped_column(Integer, ForeignKey("fee_structures.id", ondelete="CASCADE"))
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    collected_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    fee_structure = relationship("FeeStructure", backref="transactions")
    student = relationship("Student", backref="fee_transactions")
    collected_by = relationship("User", backref="collected_transactions")
    
    def __repr__(self) -> str:
        """String representation of FeeTransaction."""
        return f"<FeeTransaction {self.id}: {self.amount_paid}>" 