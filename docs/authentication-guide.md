# Le Sésame — Authentication & Authorization Guide

> Last updated: 2026-04-09

This document describes the authentication system used by Le Sésame, covering local email/password registration, Google OAuth, email verification, reCAPTCHA bot protection, and the admin user-management flow.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Authentication Methods](#authentication-methods)
   - [Local Email/Password](#local-emailpassword)
   - [Google OAuth](#google-oauth)
3. [Email Verification](#email-verification)
4. [reCAPTCHA v3 Bot Protection](#recaptcha-v3-bot-protection)
5. [JWT Tokens](#jwt-tokens)
6. [Admin User Management](#admin-user-management)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Frontend Integration](#frontend-integration)
9. [Environment Variables](#environment-variables)
10. [Security Considerations](#security-considerations)
11. [Database Schema](#database-schema)
12. [Sequence Diagrams](#sequence-diagrams)

---

## Architecture Overview

```
┌─────────────┐        ┌──────────────┐        ┌─────────────────┐
│   Frontend   │◄──────►│   Backend    │◄──────►│   PostgreSQL    │
│  (Next.js)   │  REST  │  (FastAPI)   │  async │                 │
│              │        │              │        │  users table     │
│ Google OAuth │        │ JWT + bcrypt │        │  user_activities │
│ reCAPTCHA v3 │        │ SMTP client  │        │                 │
└─────────────┘        └──────┬───────┘        └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              Google APIs  reCAPTCHA  SMTP Server
              (userinfo)   (siteverify)
```

**Key design decisions:**

| Decision | Rationale |
|---|---|
| Auto-approve on registration | Reduces friction; admins can disable users later |
| Email verification required before login | Prevents fake-email spam accounts |
| Google OAuth users skip email verification | Google already verified the email |
| reCAPTCHA v3 on all public endpoints | Invisible to users; score-based bot filtering |
| Graceful degradation | CAPTCHA, SMTP, and Google OAuth all work in dev without configuration |

---

## Authentication Methods

### Local Email/Password

**Registration flow:**

1. User fills in **username**, **email**, and **password** on the frontend.
2. Frontend obtains a reCAPTCHA v3 token (invisible, no user interaction).
3. `POST /api/auth/register` is called with all four fields.
4. Backend verifies the reCAPTCHA token with Google.
5. Backend checks username and email uniqueness.
6. Password is hashed with **bcrypt** (random salt per user).
7. User is created with `is_approved=True`, `email_verified=False`.
8. A secure random verification token (`secrets.token_urlsafe(48)`) is generated and stored with a **24-hour expiry**.
9. A verification email is sent asynchronously via SMTP.
10. Response returns a success message (no JWT token yet).

**Login flow:**

1. User enters **username** and **password**.
2. Frontend obtains a reCAPTCHA v3 token.
3. `POST /api/auth/login` is called.
4. Backend verifies reCAPTCHA, then checks credentials via bcrypt.
5. Backend checks `is_approved` (admin can disable accounts).
6. Backend checks `email_verified` — **local users must verify email before logging in**.
7. On success, a JWT token is returned.

### Google OAuth

**Flow (implicit / access-token):**

1. User clicks "Sign in with Google" on the frontend.
2. The `@react-oauth/google` library initiates Google's OAuth consent screen.
3. On success, Google returns an **access token** to the frontend.
4. Frontend obtains a reCAPTCHA v3 token.
5. `POST /api/auth/google` is called with `{ credential: <access_token>, captcha_token: <token> }`.
6. Backend verifies the reCAPTCHA token.
7. Backend verifies the Google credential:
   - **Attempt 1:** Try to verify as a Google ID token (for One Tap / credential-response flows).
   - **Attempt 2:** If that fails, call `https://www.googleapis.com/oauth2/v3/userinfo` with the token as a Bearer header.
8. Backend extracts `google_id` (sub), `email`, and `email_verified` from Google's response.
9. If the email is not verified by Google, the request is rejected.
10. Backend looks up the user:
    - **By `google_id`**: Direct match → log in.
    - **By `email`**: Account exists with same email → link Google ID to existing account, mark email as verified.
    - **No match**: Create a new account. Username is derived from the email prefix (e.g., `john.doe` from `john.doe@gmail.com`), with a numeric suffix if the name is taken.
11. All Google-authenticated users are auto-approved **and** email-verified (Google already verified the email).
12. JWT token is returned.

**Account linking:**

When a user registers with email/password and later signs in with Google using the **same email**, the accounts are automatically linked. The Google ID is stored on the existing account and email is marked as verified.

---

## Email Verification

| Property | Value |
|---|---|
| Token format | `secrets.token_urlsafe(48)` (64 URL-safe characters) |
| Token expiry | 24 hours from generation |
| Storage | `email_verification_token` + `email_verification_expires` columns on `users` table |
| Delivery | Async SMTP via `aiosmtplib` |

**Verification link format:**

```
{FRONTEND_URL}/verify-email?token={token}
```

When the user clicks the link:

1. Frontend calls `GET /api/auth/verify-email?token={token}`.
2. Backend looks up the user by token.
3. If the token is valid and not expired, `email_verified` is set to `True` and the token is cleared.
4. The user can now log in.

**Resend verification:**

`POST /api/auth/resend-verification` accepts `{ email, captcha_token }`. To prevent user enumeration, it always returns a generic success message regardless of whether the email exists.

**Admin override:**

When an admin approves a user via the admin panel, the user's email is also automatically marked as verified. This allows admins to unblock users who have trouble with email delivery.

---

## reCAPTCHA v3 Bot Protection

reCAPTCHA v3 is **invisible** — it runs in the background and assigns a score (0.0 = likely bot, 1.0 = likely human) without any user interaction.

**Protected endpoints:**

| Endpoint | Expected action |
|---|---|
| `POST /api/auth/register` | `register` |
| `POST /api/auth/login` | `login` |
| `POST /api/auth/google` | `google_auth` |
| `POST /api/auth/resend-verification` | `resend_verification` |

**Server-side verification:**

1. Frontend executes `executeRecaptcha(action)` to get a token.
2. Token is sent in the `captcha_token` field of the request body.
3. Backend posts the token to `https://www.google.com/recaptcha/api/siteverify` with the secret key.
4. Google returns `{ success, score, action }`.
5. Backend checks:
   - `success` is `true`
   - `score` ≥ configured threshold (default: **0.5**)
   - `action` matches the expected action

**Development mode:**

When `RECAPTCHA_SECRET_KEY` is not set (empty string), the CAPTCHA check always passes. This allows running in dev/test without Google credentials.

---

## JWT Tokens

| Property | Value |
|---|---|
| Algorithm | HS256 |
| Expiry | Configurable (default: **24 hours**) |
| Claims | `sub` (user ID), `username`, `role`, `exp`, `iat` |
| Transport | `Authorization: Bearer <token>` header |

The token is issued by `/auth/login` and `/auth/google` and must be included in all authenticated requests. The frontend stores it in memory (not localStorage) and includes it via an Axios interceptor.

---

## Admin User Management

Admins manage users through the admin console (`/admin`).

**Capabilities:**

| Action | Effect |
|---|---|
| **Approve/Enable** | Sets `is_approved=True` and `email_verified=True` |
| **Disapprove/Disable** | Sets `is_approved=False` — user can no longer log in or make API calls |
| **Change role** | Promote or demote users between `user` and `admin` roles |

**Admin console columns:** Username, Email, Provider (local/google), Verified, Enabled, Role, Created At, Actions.

The initial admin account is pre-seeded via environment variables (`ADMIN_USERNAME`, `ADMIN_PASSWORD`). This account is always auto-approved and email-verified.

---

## API Endpoints Reference

### Public endpoints

| Method | Path | Body | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | `{ username, password, email, captcha_token }` | Register a new local account |
| `POST` | `/api/auth/login` | `{ username, password, captcha_token }` | Login with username/password |
| `POST` | `/api/auth/google` | `{ credential, captcha_token }` | Login/register with Google |
| `GET` | `/api/auth/verify-email?token=` | — | Verify email address |
| `POST` | `/api/auth/resend-verification` | `{ email, captcha_token }` | Resend verification email |

### Authenticated endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/auth/me` | Bearer token | Get current user info |

### Response schemas

**RegisterResponse:**
```json
{
  "message": "Registration successful! Please check your email to verify your account.",
  "user": {
    "id": 1,
    "username": "johndoe",
    "role": "user",
    "is_approved": true,
    "email_verified": false,
    "auth_provider": "local",
    "created_at": "2026-04-09T12:00:00Z"
  }
}
```

**TokenResponse (login / google):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "username": "johndoe",
    "role": "user",
    "is_approved": true,
    "email_verified": true,
    "auth_provider": "local",
    "created_at": "2026-04-09T12:00:00Z"
  }
}
```

---

## Frontend Integration

### Provider wrappers

The app is wrapped with two top-level providers in `layout.tsx`:

```tsx
<AuthProviders>   {/* wraps GoogleOAuthProvider + GoogleReCaptchaProvider */}
  {children}
</AuthProviders>
```

Both providers are always mounted. When env vars are empty, they use safe fallback values so that hooks (`useGoogleLogin`, `useGoogleReCaptcha`) can be called unconditionally without conditional-hook violations.

### Login modal

The login modal (`components/auth/login-modal.tsx`) supports:

- **Tab switching** between Login and Register modes.
- **Email field** shown in Register mode.
- **Google Sign-In button** in both modes.
- **Automatic reCAPTCHA** token acquisition before every request.
- **Post-registration message** telling users to check their email.
- **Resend verification link** shown when login fails due to unverified email.

### Email verification page

`/verify-email?token=...` — a standalone page that:

1. Reads the `token` query parameter.
2. Calls the backend verify endpoint.
3. Shows a success message with a link to log in, or an error message.

### Environment variables (frontend)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `NEXT_PUBLIC_RECAPTCHA_SITE_KEY` | reCAPTCHA v3 site key |

---

## Environment Variables

### Backend

| Variable | Required | Default | Description |
|---|---|---|---|
| `GOOGLE_OAUTH_CLIENT_ID` | For Google auth | `""` | Google OAuth 2.0 client ID |
| `RECAPTCHA_SECRET_KEY` | For bot protection | `""` | reCAPTCHA v3 secret key |
| `RECAPTCHA_SCORE_THRESHOLD` | No | `0.5` | Minimum score to pass (0.0–1.0) |
| `SMTP_HOST` | For email verification | `""` | SMTP server hostname |
| `SMTP_PORT` | No | `587` | SMTP server port |
| `SMTP_USER` | For email verification | `""` | SMTP username |
| `SMTP_PASSWORD` | For email verification | `""` | SMTP password |
| `SMTP_FROM_EMAIL` | No | `noreply@lesesame.com` | Sender email address |
| `SMTP_FROM_NAME` | No | `Le Sésame` | Sender display name |
| `SMTP_USE_TLS` | No | `true` | Use STARTTLS |
| `FRONTEND_URL` | For email links | `http://localhost:3000` | Base URL of the frontend |

### Frontend

| Variable | Required | Default | Description |
|---|---|---|---|
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | For Google auth | — | Google OAuth 2.0 client ID |
| `NEXT_PUBLIC_RECAPTCHA_SITE_KEY` | For bot protection | — | reCAPTCHA v3 site key |

---

## Security Considerations

1. **Password hashing**: bcrypt with random salts — resistant to rainbow tables and GPU attacks.
2. **JWT secret**: Must be a strong random string in production (`JWT_SECRET` env var).
3. **reCAPTCHA**: Server-side only — the score is never trusted from the client. The action name is verified to prevent token reuse across endpoints.
4. **Email enumeration prevention**: The `/resend-verification` endpoint always returns the same message regardless of whether the email exists.
5. **Google token verification**: Dual verification strategy (ID token + userinfo endpoint) prevents spoofed tokens.
6. **Verification token security**: `secrets.token_urlsafe(48)` produces 64 characters of cryptographically secure randomness.
7. **Token expiry**: Verification tokens expire after 24 hours to limit the window of attack.
8. **HTTPS required**: All OAuth and CAPTCHA flows require HTTPS in production. The `Secure` flag should be set on cookies if cookie-based auth is ever added.
9. **Rate limiting**: Should be configured at the reverse proxy level (nginx/CloudFlare) for endpoints like `/register`, `/login`, and `/resend-verification`.
10. **CORS**: Configured in `main.py` — ensure only your frontend origin is allowed in production.

---

## Database Schema

The `users` table includes these auth-related columns:

| Column | Type | Default | Description |
|---|---|---|---|
| `hashed_password` | `String(255)` | `NULL` | bcrypt hash — nullable for Google-only users |
| `email` | `String(255)` | `NULL` | Unique email address |
| `auth_provider` | `String(20)` | `"local"` | `"local"` or `"google"` |
| `google_id` | `String(255)` | `NULL` | Unique Google `sub` claim — indexed |
| `email_verified` | `Boolean` | `False` | Whether email has been verified |
| `email_verification_token` | `String(255)` | `NULL` | Current verification token |
| `email_verification_expires` | `DateTime` | `NULL` | Token expiry timestamp (UTC) |
| `is_approved` | `Boolean` | `True` | Admin can set to `False` to disable |
| `role` | `String(20)` | `"user"` | `"user"` or `"admin"` |

Migration: `005_google_oauth_email_verification.py`

---

## Sequence Diagrams

### Local Registration + Email Verification

```
User          Frontend              Backend                 Google          SMTP
 │               │                     │                      │               │
 │  Fill form    │                     │                      │               │
 │──────────────►│                     │                      │               │
 │               │  executeRecaptcha() │                      │               │
 │               │─────────────────────┼─────────────────────►│               │
 │               │  captcha_token      │                      │               │
 │               │◄────────────────────┼──────────────────────│               │
 │               │                     │                      │               │
 │               │  POST /register     │                      │               │
 │               │  {user,pass,email,  │                      │               │
 │               │   captcha_token}    │                      │               │
 │               │────────────────────►│                      │               │
 │               │                     │  siteverify           │               │
 │               │                     │─────────────────────►│               │
 │               │                     │  {success, score}    │               │
 │               │                     │◄─────────────────────│               │
 │               │                     │                      │               │
 │               │                     │  Send verification   │               │
 │               │                     │──────────────────────┼──────────────►│
 │               │                     │                      │               │
 │               │  {message, user}    │                      │               │
 │               │◄────────────────────│                      │               │
 │               │                     │                      │               │
 │  Click link   │                     │                      │               │
 │──────────────►│                     │                      │               │
 │               │  GET /verify-email  │                      │               │
 │               │────────────────────►│                      │               │
 │               │  {message: "OK"}    │                      │               │
 │               │◄────────────────────│                      │               │
 │               │                     │                      │               │
 │               │  POST /login        │                      │               │
 │               │────────────────────►│                      │               │
 │               │  {access_token}     │                      │               │
 │               │◄────────────────────│                      │               │
```

### Google OAuth Login

```
User          Frontend              Backend                 Google
 │               │                     │                      │
 │  Click Google │                     │                      │
 │──────────────►│                     │                      │
 │               │  Google OAuth flow  │                      │
 │               │────────────────────────────────────────────►
 │               │  access_token       │                      │
 │               │◄────────────────────────────────────────────
 │               │                     │                      │
 │               │  executeRecaptcha() │                      │
 │               │─────────────────────┼─────────────────────►│
 │               │  captcha_token      │                      │
 │               │◄────────────────────┼──────────────────────│
 │               │                     │                      │
 │               │  POST /google       │                      │
 │               │  {credential,       │                      │
 │               │   captcha_token}    │                      │
 │               │────────────────────►│                      │
 │               │                     │  /userinfo            │
 │               │                     │─────────────────────►│
 │               │                     │  {sub,email,name}    │
 │               │                     │◄─────────────────────│
 │               │                     │                      │
 │               │  {access_token}     │                      │
 │               │◄────────────────────│                      │
```
