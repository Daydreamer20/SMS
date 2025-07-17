"""
Parent communication model definitions.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MessageType(str, Enum):
    """Enumeration for message types."""
    GENERAL = "general"
    ANNOUNCEMENT = "announcement"
    HOMEWORK = "homework"
    EXAM = "exam"
    ATTENDANCE = "attendance"
    BEHAVIOR = "behavior"
    PERFORMANCE = "performance"
    FEE = "fee"


class MessageStatus(str, Enum):
    """Enumeration for message status."""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class Message(Base):
    """Message model for parent-teacher communication."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[str] = mapped_column(String(50), default=MessageType.GENERAL.value)
    is_system_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    recipients = relationship("MessageRecipient", back_populates="message")
    
    def __repr__(self) -> str:
        """String representation of Message."""
        return f"<Message {self.id}: {self.subject}>"


class MessageRecipient(Base):
    """Message Recipient model for tracking message status per recipient."""

    __tablename__ = "message_recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default=MessageStatus.UNREAD.value)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    message_id: Mapped[int] = mapped_column(Integer, ForeignKey("messages.id", ondelete="CASCADE"))
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    message = relationship("Message", back_populates="recipients")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_messages")
    
    def __repr__(self) -> str:
        """String representation of MessageRecipient."""
        return f"<MessageRecipient {self.id}: {self.status}>"


class Thread(Base):
    """Thread model for organizing related messages."""

    __tablename__ = "threads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    student_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    creator = relationship("User", backref="created_threads")
    student = relationship("Student", backref="related_threads")
    thread_messages = relationship("ThreadMessage", back_populates="thread")
    participants = relationship("ThreadParticipant", back_populates="thread")
    
    def __repr__(self) -> str:
        """String representation of Thread."""
        return f"<Thread {self.id}: {self.title}>"


class ThreadMessage(Base):
    """Thread Message model for messages within a thread."""

    __tablename__ = "thread_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    thread_id: Mapped[int] = mapped_column(Integer, ForeignKey("threads.id", ondelete="CASCADE"))
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    thread = relationship("Thread", back_populates="thread_messages")
    sender = relationship("User", backref="thread_messages")
    
    def __repr__(self) -> str:
        """String representation of ThreadMessage."""
        return f"<ThreadMessage {self.id}>"


class ThreadParticipant(Base):
    """Thread Participant model for tracking participants in a thread."""

    __tablename__ = "thread_participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    last_read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    thread_id: Mapped[int] = mapped_column(Integer, ForeignKey("threads.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    thread = relationship("Thread", back_populates="participants")
    user = relationship("User", backref="thread_participations")
    
    def __repr__(self) -> str:
        """String representation of ThreadParticipant."""
        return f"<ThreadParticipant {self.id}>"


class Announcement(Base):
    """Announcement model for school-wide or class-specific announcements."""

    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    target_audience: Mapped[str] = mapped_column(String(50))  # all, teachers, parents, students
    publish_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    class_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    creator = relationship("User", backref="created_announcements")
    class_ = relationship("Class", backref="announcements")
    
    def __repr__(self) -> str:
        """String representation of Announcement."""
        return f"<Announcement {self.id}: {self.title}>" 