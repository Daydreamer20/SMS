"""
Database models package.

This module imports all models to make them available when importing from app.models.
"""

from app.models.user import User, Role
from app.models.student import Student, ParentGuardian, Gender, BloodGroup
from app.models.staff import Staff, StaffType
from app.models.academic import (
    AcademicYear, Class, Subject, 
    Examination, ExaminationSubject, Grade, GradingScale,
    ExaminationType, GradeStatus
)
from app.models.settings import SchoolSettings, SystemSettings, GradingSystem
from app.models.library import (
    Book, BookCategory, BookIssue, BookReservation,
    BookStatus, LibrarySettings
)
from app.models.calendar import (
    CalendarEvent, EventAttendee, CalendarIntegration,
    EventType, RecurrenceType
)
from app.models.email import (
    EmailTemplate, EmailNotification, EmailSettings, EmailSubscription,
    EmailStatus, EmailType
)
from app.models.parent_communication import (
    Message, MessageRecipient, Thread, ThreadMessage, ThreadParticipant, Announcement,
    MessageType, MessageStatus
)
from app.models.fees import (
    FeeCategory, FeeStructure, FeeTransaction, FeeDueDate, 
    PaymentMethod, PaymentStatus
)
from app.models.timetable import (
    Timetable, TimetableEntry, Period, DayOfWeek
)
from app.models.integrations import (
    ExternalApplication, APIKey, WebhookEndpoint, IntegrationLog,
    IntegrationType, LogLevel
) 