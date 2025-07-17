"""
Dependencies for FastAPI dependency injection system.
"""

from typing import Generator, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.schemas.user import TokenPayload


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Get the current authenticated user.

    Args:
        db: Database session
        token: JWT token from OAuth2 scheme

    Returns:
        User: Current user

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Decode the token
        payload = decode_token(token)
        user_id: str = payload.sub
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get the user from the database
    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user: Optional[User] = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user is inactive
    """
    return current_user


async def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active superuser (admin).

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current active superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


def check_roles(required_roles: List[str]) -> callable:
    """
    Create a dependency that checks if the user has the required roles.

    Args:
        required_roles: List of role names required for access

    Returns:
        callable: Dependency function
    """
    async def has_roles(
        token: str = Depends(oauth2_scheme),
    ) -> bool:
        """
        Check if the user has the required roles.

        Args:
            token: JWT token

        Returns:
            bool: True if user has required roles

        Raises:
            HTTPException: If user doesn't have required roles
        """
        try:
            payload = decode_token(token)
            user_roles = payload.roles
            
            # Check if any of the required roles are in user roles
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {required_roles}",
                )
            return True
        except (JWTError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    return has_roles


# Common role-based dependencies
async def get_current_admin(
    current_user: User = Depends(get_current_user),
    has_role: bool = Depends(check_roles(["admin"])),
) -> User:
    """Get current user with admin role."""
    return current_user


async def get_current_teacher(
    current_user: User = Depends(get_current_user),
    has_role: bool = Depends(check_roles(["teacher", "admin"])),
) -> User:
    """Get current user with teacher or admin role."""
    return current_user


async def get_current_student(
    current_user: User = Depends(get_current_user),
    has_role: bool = Depends(check_roles(["student"])),
) -> User:
    """Get current user with student role."""
    return current_user 