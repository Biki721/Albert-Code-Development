"""
Authentication and session management with exclusive single-user lock
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
from pathlib import Path
import threading
import asyncio

from .config import settings
from .models import Token, AuthStatus, UserLogin


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token
security = HTTPBearer()


class SessionLock:
    """
    Manages exclusive single-user session lock with timeout
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._current_user: Optional[str] = None
        self._lock_time: Optional[datetime] = None
        self._last_activity: Optional[datetime] = None
        
    def acquire(self, email: str) -> bool:
        """
        Attempt to acquire the lock for a user
        Returns True if successful, False if locked by another user
        """
        with self._lock:
            # Check if lock expired
            if self._is_expired():
                self._release_internal()
            
            # If no one has lock or same user, grant access
            if self._current_user is None or self._current_user == email:
                self._current_user = email
                self._lock_time = datetime.utcnow()
                self._last_activity = datetime.utcnow()
                return True
            
            return False
    
    def release(self, email: str) -> bool:
        """
        Release the lock if held by this user
        """
        with self._lock:
            if self._current_user == email:
                self._release_internal()
                return True
            return False
    
    def _release_internal(self):
        """Internal release without lock check"""
        self._current_user = None
        self._lock_time = None
        self._last_activity = None
    
    def update_activity(self, email: str):
        """Update last activity timestamp"""
        with self._lock:
            if self._current_user == email:
                self._last_activity = datetime.utcnow()
    
    def _is_expired(self) -> bool:
        """Check if current lock has expired due to inactivity"""
        if self._last_activity is None:
            return False
        
        timeout_seconds = settings.SESSION_LOCK_TIMEOUT
        elapsed = (datetime.utcnow() - self._last_activity).total_seconds()
        return elapsed > timeout_seconds
    
    def get_status(self) -> AuthStatus:
        """Get current lock status"""
        with self._lock:
            if self._is_expired():
                self._release_internal()
            
            return AuthStatus(
                authenticated=self._current_user is not None,
                user_email=self._current_user,
                locked_by=self._current_user,
                lock_expires_at=self._get_expiry_time()
            )
    
    def _get_expiry_time(self) -> Optional[datetime]:
        """Calculate when lock will expire"""
        if self._last_activity is None:
            return None
        return self._last_activity + timedelta(seconds=settings.SESSION_LOCK_TIMEOUT)


# Global session lock instance
session_lock = SessionLock()


class UserManager:
    """Manages user credentials"""
    
    def __init__(self, users_file: Path):
        self.users_file = users_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create users file if it doesn't exist"""
        if not self.users_file.exists():
            self.users_file.parent.mkdir(parents=True, exist_ok=True)
            # Create with default admin user
            default_users = {
                "admin@hpe.com": {
                    "email": "admin@hpe.com",
                    "hashed_password": self._hash_password("Admin@123"),
                    "full_name": "Admin User",
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            self._save_users(default_users)
    
    def _load_users(self) -> Dict:
        """Load users from file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_users(self, users: Dict):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user
        Returns user dict if valid, None otherwise
        """
        email_lower = email.lower()
        allowed_domain = settings.ALLOWED_EMAIL_DOMAIN.lower()

        # Enforce allowed email domain (e.g. only @hpe.com)
        if not email_lower.endswith(f"@{allowed_domain}"):
            return None

        # Enforce single shared login password for all users
        if password != settings.SHARED_LOGIN_PASSWORD:
            return None

        users = self._load_users()
        user = users.get(email)

        # Auto-create user record if it doesn't exist yet
        if not user:
            user = {
                "email": email,
                "full_name": email.split("@")[0],
                "created_at": datetime.utcnow().isoformat(),
            }
            users[email] = user
            self._save_users(users)

        return user
    
    def create_user(self, email: str, password: str, full_name: str) -> bool:
        """Create a new user"""
        users = self._load_users()
        
        if email in users:
            return False
        
        users[email] = {
            "email": email,
            "hashed_password": self._hash_password(password),
            "full_name": full_name,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self._save_users(users)
        return True
    
    def get_user(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        users = self._load_users()
        return users.get(email)


# Global user manager
user_manager = UserManager(settings.USERS_FILE)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return email if valid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to get current authenticated user from token
    Raises HTTP 401 if invalid
    """
    token = credentials.credentials
    email = verify_token(token)
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user exists
    user = user_manager.get_user(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Update activity timestamp
    session_lock.update_activity(email)
    
    return email


async def require_session_lock(email: str = Depends(get_current_user)) -> str:
    """
    Dependency that requires the user to hold the exclusive session lock
    """
    status_info = session_lock.get_status()
    
    if not status_info.authenticated or status_info.user_email != email:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"System is locked by {status_info.locked_by}. Please ask them to logout.",
        )
    
    return email


def login_user(login_data: UserLogin) -> Token:
    """
    Authenticate user and create session lock
    """
    # Authenticate
    user = user_manager.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Try to acquire lock
    if not session_lock.acquire(login_data.email):
        lock_status = session_lock.get_status()
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"{lock_status.locked_by} is currently logged in. Please ask them to logout.",
        )
    
    # Create token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.email},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def logout_user(email: str) -> bool:
    """
    Logout user and release session lock
    """
    return session_lock.release(email)
