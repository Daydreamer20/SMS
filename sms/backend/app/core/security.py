"""
Security utilities for authentication and authorization.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.user import TokenPayload


# Password hashing context
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        bool: True if password matches hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, int], expires_delta: Optional[timedelta] = None, roles: List[str] = []
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: Subject (usually user ID)
        expires_delta: Optional expiration time
        roles: List of role names

    Returns:
        str: JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: Dict[str, Any] = {"exp": expire, "sub": str(subject), "roles": roles}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: Union[str, int]) -> str:
    """
    Create a JWT refresh token.

    Args:
        subject: Subject (usually user ID)

    Returns:
        str: JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: Dict[str, Any] = {"exp": expire, "sub": str(subject), "refresh": True}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> TokenPayload:
    """
    Decode a JWT token.

    Args:
        token: JWT token

    Returns:
        TokenPayload: Decoded token payload

    Raises:
        ValueError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        raise ValueError(f"Invalid token: {str(e)}") 