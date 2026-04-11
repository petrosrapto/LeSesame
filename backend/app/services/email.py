"""
Le Sésame Backend - Email Verification Service

Sends verification emails via SMTP (async).

Author: Petros Raptopoulos
"""

import secrets
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from ..core import settings, logger


# Token validity duration
VERIFICATION_TOKEN_EXPIRY_HOURS = 24


def generate_verification_token() -> str:
    """Generate a cryptographically secure email verification token."""
    return secrets.token_urlsafe(48)


def verification_expiry() -> datetime:
    """Return the expiry datetime for a new verification token."""
    return datetime.utcnow() + timedelta(hours=VERIFICATION_TOKEN_EXPIRY_HOURS)


def build_verification_url(token: str) -> str:
    """Build the frontend email-verification URL."""
    base = settings.frontend_url.rstrip("/")
    return f"{base}/verify-email?token={token}"


def _build_verification_email(to_email: str, username: str, verify_url: str) -> MIMEMultipart:
    """Build the HTML verification email."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg["Subject"] = "Verify your Le Sésame account"

    plain = (
        f"Hi {username},\n\n"
        f"Please verify your email by visiting:\n{verify_url}\n\n"
        f"This link expires in {VERIFICATION_TOKEN_EXPIRY_HOURS} hours.\n\n"
        "If you didn't create an account, you can ignore this email.\n\n"
        "— Le Sésame"
    )

    html = f"""\
    <html>
    <body style="font-family: Arial, sans-serif; background: #1a1a2e; color: #e0e0e0; padding: 40px 0;">
      <div style="max-width: 480px; margin: 0 auto; background: #16213e; border: 2px solid #f97316; padding: 32px;">
        <h1 style="color: #f97316; font-size: 20px; margin-bottom: 16px;">🔐 Le Sésame</h1>
        <p>Hi <strong>{username}</strong>,</p>
        <p>Please verify your email to activate your account:</p>
        <div style="text-align: center; margin: 28px 0;">
          <a href="{verify_url}" style="background: #f97316; color: #fff; padding: 12px 32px; text-decoration: none; font-weight: bold; border: 2px solid #ea580c;">
            Verify Email
          </a>
        </div>
        <p style="font-size: 13px; color: #aaa;">
          This link expires in {VERIFICATION_TOKEN_EXPIRY_HOURS} hours.<br>
          If you didn't sign up, please ignore this email.
        </p>
      </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))
    return msg


async def send_verification_email(to_email: str, username: str, token: str) -> bool:
    """Send an email-verification message.

    Returns True on success, False on failure (logs errors internally).
    """
    if not settings.smtp_host:
        logger.warning("SMTP not configured – skipping verification email")
        return False

    verify_url = build_verification_url(token)
    msg = _build_verification_email(to_email, username, verify_url)

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            start_tls=settings.smtp_use_tls and not settings.smtp_use_ssl,
            use_tls=settings.smtp_use_ssl,
        )
        logger.info(f"Verification email sent to {to_email}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send verification email to {to_email}: {exc}")
        return False
