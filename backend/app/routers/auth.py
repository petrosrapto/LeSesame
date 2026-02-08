"""
Le Sésame Backend - Authentication Router

Author: Petros Raptopoulos
Date: 2026/02/06
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
import jwt

from ..db import get_db, User, UserRepository, UserActivity
from ..schemas import (
    UserCreate, UserResponse, TokenResponse, LoginRequest, RegisterResponse,
)
from ..core import settings, logger

router = APIRouter()

# JWT Security
security = HTTPBearer(auto_error=False)


def create_access_token(user_id: int, username: str, role: str = "user") -> tuple[str, int]:
    """Create a JWT access token."""
    expires_delta = timedelta(hours=settings.jwt_expiration_hours)
    expire = datetime.now(timezone.utc) + expires_delta
    
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, int(expires_delta.total_seconds())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def hash_password(password: str) -> str:
    """Hash a password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def _client_ip(request: Request) -> str:
    """Extract client IP from request."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def log_activity(
    db: AsyncSession, user_id: int, action: str, detail: str | None = None, ip: str | None = None,
) -> None:
    """Log a user activity entry."""
    entry = UserActivity(user_id=user_id, action=action, detail=detail, ip_address=ip)
    db.add(entry)
    await db.flush()


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user from JWT token."""
    if not credentials:
        return None
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        user_id = int(payload.get("sub"))
        
        repo = UserRepository(db)
        user = await repo.get_by_id(user_id)
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


async def require_user(
    user: Annotated[Optional[User], Depends(get_current_user)]
) -> User:
    """Require authenticated user."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_approved_user(
    user: Annotated[User, Depends(require_user)]
) -> User:
    """Require an authenticated AND approved user."""
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending admin approval.",
        )
    return user


async def require_admin(
    user: Annotated[User, Depends(require_user)]
) -> User:
    """Require an admin user."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


@router.post("/register", response_model=RegisterResponse)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user. Account must be approved by an admin before login."""
    repo = UserRepository(db)
    
    # Check if username exists
    if await repo.username_exists(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists (when provided)
    if user_data.email and await repo.email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user (not approved — admin must approve)
    user = await repo.create_user(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        email=user_data.email,
        role="user",
        is_approved=False,
    )
    
    await log_activity(db, user.id, "register", ip=_client_ip(request))
    
    logger.info(f"User registered (pending approval): {user.username}")
    
    return RegisterResponse(
        message="Registration successful! Your account is pending admin approval. You will be able to log in once an administrator approves your account.",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Login with username and password."""
    repo = UserRepository(db)
    user = await repo.get_by_username(login_data.username)
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check approval
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending admin approval. Please wait."
        )
    
    token, expires_in = create_access_token(user.id, user.username, user.role)
    
    await log_activity(db, user.id, "login", ip=_client_ip(request))
    
    logger.info(f"User logged in: {user.username}")
    
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: Annotated[User, Depends(require_user)]):
    """Get current user information."""
    return UserResponse.model_validate(user)
