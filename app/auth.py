import hashlib
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import models
from .database import get_db
import os
from dotenv import load_dotenv
load_dotenv()

# ============================================
# Security Configuration
# ============================================
  # ← Added int() and default
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # ← Added default
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))
# Validate SECRET_KEY exists
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in .env file")

# HTTP Bearer token security
security = HTTPBearer()

# ============================================
# JWT TOKEN
# ============================================

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing user data to encode in token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Fixed: Use the variable, not the string!
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================
# Authentication Dependency
# ============================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency to get the current authenticated user from JWT token.
    This protects endpoints that require authentication.
    
    Usage in endpoint:
        current_user: models.User = Depends(get_current_user)
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        
    Returns:
        User object from database
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Retrieve user from database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
        
    return user

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with salt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string with salt
    """
    # Generate a random salt
    salt = secrets.token_hex(16)
    
    # Combine password and salt, then hash
    pwd_with_salt = password + salt
    hashed = hashlib.sha256(pwd_with_salt.encode()).hexdigest()
    
    # Return format: salt$hash
    return f"{salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Split the stored hash to get salt and hash
        salt, stored_hash = hashed_password.split("$")
        
        # Hash the provided password with the same salt
        pwd_with_salt = plain_password + salt
        new_hash = hashlib.sha256(pwd_with_salt.encode()).hexdigest()
        
        # Compare hashes
        return new_hash == stored_hash
    except (ValueError, AttributeError):
        return False
