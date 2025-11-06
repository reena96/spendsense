"""JWT token generation and validation."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from dataclasses import dataclass

from jose import JWTError, jwt

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_secret_key_change_in_production_12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days


@dataclass
class TokenData:
    """Token payload data."""

    operator_id: str
    username: str
    role: str
    token_type: str  # 'access' or 'refresh'


def create_access_token(operator_id: str, username: str, role: str) -> str:
    """
    Create a JWT access token.

    Args:
        operator_id: Operator ID
        username: Operator username
        role: Operator role

    Returns:
        Encoded JWT token string
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": operator_id,
        "username": username,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(operator_id: str, username: str, role: str) -> str:
    """
    Create a JWT refresh token.

    Args:
        operator_id: Operator ID
        username: Operator username
        role: Operator role

    Returns:
        Encoded JWT token string
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": operator_id,
        "username": username,
        "role": role,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, expected_type: str = "access") -> Optional[TokenData]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string
        expected_type: Expected token type ('access' or 'refresh')

    Returns:
        TokenData if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        operator_id: str = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")
        token_type: str = payload.get("type")

        if not operator_id or not username or not role or not token_type:
            return None

        if token_type != expected_type:
            return None

        return TokenData(
            operator_id=operator_id,
            username=username,
            role=role,
            token_type=token_type,
        )
    except JWTError:
        return None


def decode_token_unsafe(token: str) -> Optional[dict]:
    """
    Decode token without verification (for inspection only).

    WARNING: This does not verify the token signature or expiration.
    Use only for debugging or inspection purposes.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload if decodable, None otherwise
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
    except JWTError:
        return None
