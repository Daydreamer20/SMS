"""
Authentication API endpoints.
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User, Role
from app.schemas.user import Token, UserCreate, User as UserSchema


router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Check if user exists
    result = await db.execute(
        select(User).filter(
            (User.username == form_data.username) | (User.email == form_data.username)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user roles
    roles = [role.name for role in user.roles]
    
    # Generate access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires, roles=roles
    )
    
    # Generate refresh token
    refresh_token = create_refresh_token(subject=user.id)
    
    # Calculate expiration timestamp
    expires_at = int((datetime.utcnow() + access_token_expires).timestamp())
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_at": expires_at,
    }


@router.post("/register", response_model=UserSchema)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Register a new user.
    """
    # Check if username already exists
    result = await db.execute(select(User).filter(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check if email already exists
    result = await db.execute(select(User).filter(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=True,
        is_verified=False,
    )
    
    # Add user to database
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Add default student role
    result = await db.execute(select(Role).filter(Role.name == "student"))
    student_role = result.scalar_one_or_none()
    
    if not student_role:
        student_role = Role(name="student", description="Student role")
        db.add(student_role)
        await db.commit()
        await db.refresh(student_role)
    
    db_user.roles.append(student_role)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user 