"""
API v1 router configuration.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, students, staff, examinations, settings, library
from app.api.v1.endpoints import calendar, email, parent_communication, fees, timetable, integrations
from app.api.v1.endpoints.timetable import router as timetable_router


api_router = APIRouter()

# Include routers from endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(staff.router, prefix="/staff", tags=["staff"])
api_router.include_router(examinations.router, prefix="/examinations", tags=["examinations"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(library.router, prefix="/library", tags=["library"])

# Integration routers
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(email.router, prefix="/email", tags=["email"])
api_router.include_router(parent_communication.router, prefix="/parent-communication", tags=["parent_communication"])
api_router.include_router(fees.router, prefix="/fees", tags=["fees"])
api_router.include_router(timetable_router, prefix="/timetable", tags=["timetable"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"]) 