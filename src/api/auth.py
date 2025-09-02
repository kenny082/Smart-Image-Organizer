"""
Authentication module for the API.
Handles API key verification and JWT token management.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
API_KEY = os.getenv("API_KEY", "your-api-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security contexts
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
api_key_header = APIKeyHeader(name="X-API-Key")


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing data to encode in the token

    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Dict: Decoded token data

    Raises:
        HTTPException: If token is invalid
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key from the request header.

    Args:
        api_key: API key from request header

    Returns:
        str: Verified API key

    Raises:
        HTTPException: If API key is invalid
    """
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key
