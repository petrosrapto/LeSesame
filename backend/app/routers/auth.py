"""
Le Sésame Backend - Authentication Router

Supports:
- Local registration with email verification
- Google OAuth login/register
- reCAPTCHA v3 on all public endpoints

Author: Petros Raptopoulos
Date: 2026/02/06
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
import jwt

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
import httpx as _httpx

from ..db import get_db, User, UserRepository, UserActivity
from ..schemas import (
    UserCreate, UserResponse, TokenResponse, LoginRequest, RegisterResponse,
    GoogleAuthRequest, ResendVerificationRequest,
)
from ..core import settings, logger
from ..services.captcha import verify_recaptcha
from ..services.email import (
    generate_verification_token, verification_expiry, send_verification_email,
)

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
    """Require an authenticated AND approved (enabled) user."""
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been disabled. Contact an administrator.",
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
    """Register a new user with email verification."""
    # Verify reCAPTCHA
    if not await verify_recaptcha(user_data.captcha_token, expected_action="register"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CAPTCHA verification failed. Please try again.",
        )

    repo = UserRepository(db)
    
    # Check if username exists
    if await repo.username_exists(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if await repo.email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Generate email verification token
    token = generate_verification_token()
    
    # Create user (auto-approved but email NOT verified)
    user = await repo.create_user(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        email=user_data.email,
        role="user",
        is_approved=True,
        auth_provider="local",
        email_verified=False,
        email_verification_token=token,
        email_verification_expires=verification_expiry(),
    )
    
    await log_activity(db, user.id, "register", ip=_client_ip(request))

    # Send verification email (non-blocking — failure logged but doesn't block response)
    await send_verification_email(user_data.email, user_data.username, token)
    
    logger.info(f"User registered (pending email verification): {user.username}")
    
    return RegisterResponse(
        message="Registration successful! Please check your email to verify your account.",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Login with username and password."""
    # Verify reCAPTCHA
    if not await verify_recaptcha(login_data.captcha_token, expected_action="login"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CAPTCHA verification failed. Please try again.",
        )

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
            detail="Your account has been disabled. Contact an administrator."
        )

    # Check email verification (local auth only)
    if user.auth_provider == "local" and not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in. Check your inbox for a verification link.",
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


# ───────────────────── Google OAuth ──────────────────────


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    data: GoogleAuthRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Login or register with a Google account.

    The frontend sends the Google ID-token (``credential``).
    The backend verifies it with Google, then either logs in
    the existing user or creates a new account.
    """
    # Verify reCAPTCHA
    if not await verify_recaptcha(data.captcha_token, expected_action="google_auth"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CAPTCHA verification failed. Please try again.",
        )

    if not settings.google_oauth_client_id:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google sign-in is not configured on this server.",
        )

    # Verify the Google credential.
    # The frontend may send either a Google ID-token (from One Tap / credential flow)
    # or an access_token (from the implicit OAuth flow).
    # We try ID-token verification first; on failure we try the tokeninfo endpoint.
    google_id: str | None = None
    email: str | None = None
    email_verified_by_google: bool = False
    name: str | None = None

    # Attempt 1: verify as ID token
    try:
        idinfo = google_id_token.verify_oauth2_token(
            data.credential,
            google_requests.Request(),
            settings.google_oauth_client_id,
        )
        google_id = idinfo["sub"]
        email = idinfo.get("email", "")
        email_verified_by_google = idinfo.get("email_verified", False)
        name = idinfo.get("name", "")
    except ValueError:
        # Attempt 2: treat as access_token, verify via Google's userinfo endpoint
        try:
            async with _httpx.AsyncClient(timeout=10) as hc:
                resp = await hc.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {data.credential}"},
                )
                if resp.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Google credential",
                    )
                uinfo = resp.json()
                google_id = uinfo.get("sub")
                email = uinfo.get("email", "")
                email_verified_by_google = uinfo.get("email_verified", False)
                name = uinfo.get("name", "")
        except _httpx.HTTPError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not verify Google credential",
            )

    if not email or not email_verified_by_google:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A verified Google email is required.",
        )

    repo = UserRepository(db)

    # Try to find existing user by google_id first, then by email
    user = await repo.get_by_google_id(google_id)

    if not user:
        user = await repo.get_by_email(email)
        if user:
            # An account with this email exists — link Google ID
            if user.auth_provider == "local" and not user.google_id:
                user.google_id = google_id
                user.email_verified = True  # Google verified the email
                user = await repo.update(user)
            elif user.google_id and user.google_id != google_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This email is already linked to a different Google account.",
                )

    if not user:
        # Create a new account — derive username from email prefix
        base_username = email.split("@")[0][:40]
        username = base_username
        counter = 1
        while await repo.username_exists(username):
            username = f"{base_username}_{counter}"
            counter += 1

        user = await repo.create_user(
            username=username,
            email=email,
            role="user",
            is_approved=True,
            auth_provider="google",
            google_id=google_id,
            email_verified=True,  # Google verified the email
        )
        await log_activity(db, user.id, "register", detail="google_oauth", ip=_client_ip(request))
        logger.info(f"User registered via Google: {user.username}")

    # Check that the user isn't disabled by admin
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been disabled. Contact an administrator.",
        )

    token, expires_in = create_access_token(user.id, user.username, user.role)
    await log_activity(db, user.id, "login", detail="google_oauth", ip=_client_ip(request))

    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


# ───────────────────── Email Verification ──────────────────────


@router.get("/verify-email")
async def verify_email(
    token: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """Verify a user's email address using the token sent via email."""
    repo = UserRepository(db)
    user = await repo.get_by_verification_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link.",
        )

    if user.email_verification_expires and user.email_verification_expires.replace(
        tzinfo=timezone.utc
    ) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification link has expired. Please request a new one.",
        )

    await repo.verify_email(user)
    logger.info(f"Email verified for user: {user.username}")

    return {"message": "Email verified successfully! You can now log in."}


@router.post("/resend-verification")
async def resend_verification(
    data: ResendVerificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Resend the email verification link."""
    # Verify reCAPTCHA
    if not await verify_recaptcha(data.captcha_token, expected_action="resend_verification"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CAPTCHA verification failed. Please try again.",
        )

    repo = UserRepository(db)
    user = await repo.get_by_email(data.email)

    # Always return success to avoid user enumeration
    if not user or user.email_verified or user.auth_provider != "local":
        return {"message": "If that email is registered and unverified, a new link has been sent."}

    token = generate_verification_token()
    await repo.set_verification_token(user, token, verification_expiry())
    await send_verification_email(user.email, user.username, token)

    return {"message": "If that email is registered and unverified, a new link has been sent."}
