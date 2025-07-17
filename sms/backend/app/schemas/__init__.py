"""
Pydantic schema package.

This module imports all schemas to make them available when importing from app.schemas.
"""

# Import schemas here to make them available from app.schemas
from app.schemas.user import (
    User, UserCreate, UserUpdate, Role, RoleCreate, RoleUpdate, UserLogin, Token
)
from app.schemas.student import (
    Student, StudentCreate, StudentUpdate, StudentWithClass,
    ParentGuardian, ParentGuardianCreate, ParentGuardianUpdate
)
from app.schemas.staff import (
    Staff, StaffCreate, StaffUpdate, StaffWithUser, StaffWithClasses
)
from app.schemas.academic import (
    Class, ClassCreate, ClassUpdate, ClassWithAcademicYear, ClassWithSubjects,
    Subject, SubjectCreate, SubjectUpdate,
    AcademicYear, AcademicYearCreate, AcademicYearUpdate,
    Examination, ExaminationCreate, ExaminationUpdate,
    ExaminationSubject, ExaminationSubjectCreate, ExaminationSubjectUpdate, ExaminationSubjectWithDetails,
    Grade, GradeCreate, GradeUpdate, GradeWithDetails,
    GradingScale, GradingScaleCreate, GradingScaleUpdate
)
from app.schemas.settings import (
    SchoolSettings, SchoolSettingsCreate, SchoolSettingsUpdate,
    SystemSettings, SystemSettingsCreate, SystemSettingsUpdate,
    GradingSystem, GradingSystemCreate, GradingSystemUpdate
)
from app.schemas.library import (
    Book, BookCreate, BookUpdate, BookWithCategory,
    BookCategory, BookCategoryCreate, BookCategoryUpdate,
    BookIssue, BookIssueCreate, BookIssueUpdate, BookIssueWithDetails,
    BookReservation, BookReservationCreate, BookReservationUpdate, BookReservationWithDetails,
    LibrarySettingsBase
) 