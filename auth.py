from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import bcrypt

from database import get_db
from models import User
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

__all__ = ["pwd_context", "create_access_token", "verify_token", "verify_password", "get_password_hash", "get_current_user"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash (supports both passlib and direct bcrypt)."""
    try:
        if isinstance(plain_password, str):
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
        
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except (ValueError, Exception):
            try:
                if isinstance(hashed_password, str):
                    hashed_bytes = hashed_password.encode('utf-8')
                else:
                    hashed_bytes = hashed_password
                
                password_bytes_final = plain_password.encode('utf-8')
                if len(password_bytes_final) > 72:
                    password_bytes_final = password_bytes_final[:72]
                
                return bcrypt.checkpw(password_bytes_final, hashed_bytes)
            except Exception:
                return False
    except (ValueError, Exception) as e:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using passlib/bcrypt with fallback to direct bcrypt."""
    if not isinstance(password, str):
        password = str(password)
    
    password_bytes = password.encode('utf-8')
    
    if len(password_bytes) > 71:
        password = password_bytes[:71].decode('utf-8', errors='ignore')
    
    if not password:
        raise ValueError("Password cannot be empty after truncation")
    
    final_bytes = password.encode('utf-8')
    if len(final_bytes) > 72:
        password = final_bytes[:71].decode('utf-8', errors='ignore')
        if not password:
            raise ValueError("Password becomes empty after forced truncation")
    
    try:
        return pwd_context.hash(password)
    except (ValueError, Exception) as e:
        error_msg = str(e).lower()
        if "72 bytes" in error_msg or "too long" in error_msg or "truncate" in error_msg:
            try:
                salt = bcrypt.gensalt()
                password_bytes_final = password.encode('utf-8')
                if len(password_bytes_final) > 72:
                    password_bytes_final = password_bytes_final[:72]
                hashed = bcrypt.hashpw(password_bytes_final, salt)
                return hashed.decode('utf-8')
            except Exception as e2:
                raise ValueError(f"Failed to hash password with both passlib and direct bcrypt: {str(e2)}")
        raise ValueError(f"Password hashing failed: {str(e)}")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Dependency to get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

