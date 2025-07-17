"""
Schemas for academic data validation.
"""

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, validator

# Subject schemas
class SubjectBase(BaseModel):
    """Base schema for Subject."""
    name: str
    code: str
    description: Optional[str] = None
    credits: Optional[int] = None
    is_active: bool = True


class SubjectCreate(SubjectBase):
    """Schema for creating a Subject."""
    pass


class SubjectUpdate(SubjectBase):
    """Schema for updating a Subject."""
    name: Optional[str] = None
    code: Optional[str] = None


class Subject(SubjectBase):
    """Schema for a Subject."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Config for Subject schema."""
        from_attributes = True


# Class schemas
class ClassBase(BaseModel):
    """Base schema for Class."""
    name: str
    section: Optional[str] = None
    academic_year: str
    description: Optional[str] = None
    is_active: bool = True
    teacher_id: Optional[int] = None


class ClassCreate(ClassBase):
    """Schema for creating a Class."""
    pass


class ClassUpdate(ClassBase):
    """Schema for updating a Class."""
    name: Optional[str] = None
    section: Optional[str] = None
    academic_year: Optional[str] = None


class Class(ClassBase):
    """Schema for a Class."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Config for Class schema."""
        from_attributes = True


class ClassWithStudents(Class):
    """Schema for a Class with students."""
    students: List["StudentSchema"] = []

    class Config:
        """Config for ClassWithStudents schema."""
        from_attributes = True


# Grade schemas
class GradeBase(BaseModel):
    """Base schema for Grade."""
    value: float
    max_value: float = 100.0
    grade_type: str
    term: Optional[str] = None
    description: Optional[str] = None
    graded_date: datetime = Field(default_factory=datetime.utcnow)
    student_id: int
    subject_id: int


class GradeCreate(GradeBase):
    """Schema for creating a Grade."""
    pass


class GradeUpdate(GradeBase):
    """Schema for updating a Grade."""
    value: Optional[float] = None
    max_value: Optional[float] = None
    grade_type: Optional[str] = None
    term: Optional[str] = None
    description: Optional[str] = None
    graded_date: Optional[datetime] = None
    student_id: Optional[int] = None
    subject_id: Optional[int] = None


class Grade(GradeBase):
    """Schema for a Grade."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Config for Grade schema."""
        from_attributes = True


# Examination schemas
class ExaminationBase(BaseModel):
    """Base schema for Examination."""
    name: str
    exam_type: str
    start_date: date
    end_date: date
    description: Optional[str] = None
    is_published: bool = False


class ExaminationCreate(ExaminationBase):
    """Schema for creating an Examination."""
    pass


class ExaminationUpdate(ExaminationBase):
    """Schema for updating an Examination."""
    name: Optional[str] = None
    exam_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_published: Optional[bool] = None


class Examination(ExaminationBase):
    """Schema for an Examination."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Config for Examination schema."""
        from_attributes = True


# StudentPerformanceReport schemas
class StudentPerformanceReportBase(BaseModel):
    """Base schema for StudentPerformanceReport."""
    term: str
    academic_year: str
    overall_grade: Optional[float] = None
    overall_percentage: Optional[float] = None
    attendance_percentage: Optional[float] = None
    remarks: Optional[str] = None
    teacher_comments: Optional[str] = None
    principal_comments: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    is_published: bool = False
    published_date: Optional[datetime] = None
    student_id: int
    class_id: int


class StudentPerformanceReportCreate(StudentPerformanceReportBase):
    """Schema for creating a StudentPerformanceReport."""
    pass


class StudentPerformanceReportUpdate(StudentPerformanceReportBase):
    """Schema for updating a StudentPerformanceReport."""
    term: Optional[str] = None
    academic_year: Optional[str] = None
    overall_grade: Optional[float] = None
    overall_percentage: Optional[float] = None
    attendance_percentage: Optional[float] = None
    remarks: Optional[str] = None
    teacher_comments: Optional[str] = None
    principal_comments: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    is_published: Optional[bool] = None
    published_date: Optional[datetime] = None
    student_id: Optional[int] = None
    class_id: Optional[int] = None


class StudentPerformanceReport(StudentPerformanceReportBase):
    """Schema for a StudentPerformanceReport."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Config for StudentPerformanceReport schema."""
        from_attributes = True


class StudentPerformanceReportDetail(StudentPerformanceReport):
    """Schema for a StudentPerformanceReport with detailed student and class info."""
    class_: Class
    student: "StudentSchema"

    class Config:
        """Config for StudentPerformanceReportDetail schema."""
        from_attributes = True


from app.schemas.student import Student as StudentSchema

# Update forward refs
ClassWithStudents.model_rebuild()
StudentPerformanceReportDetail.model_rebuild() 