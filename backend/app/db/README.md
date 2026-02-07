# Database Schema

This document describes the database schema for Le Sésame backend.

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │  game_sessions  │       │ level_attempts  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──┐   │ id (PK)         │◄──┐   │ id (PK)         │
│ username        │   │   │ user_id (FK)────│───┘   │ session_id (FK)─│───┐
│ email           │   │   │ session_token   │       │ level           │   │
│ hashed_password │   │   │ current_level   │       │ attempts        │   │
│ created_at      │   │   │ started_at      │       │ messages_sent   │   │
└─────────────────┘   │   │ last_activity   │       │ completed       │   │
        │             │   │ is_active       │       │ completed_at    │   │
        │             │   └─────────────────┘       │ time_spent_sec  │   │
        │             │           │                 │ started_at      │   │
        │             │           │                 └─────────────────┘   │
        │             │           │                                       │
        │             │           ▼                                       │
        │             │   ┌─────────────────┐                             │
        │             │   │  chat_messages  │                             │
        │             │   ├─────────────────┤                             │
        │             │   │ id (PK)         │                             │
        │             │   │ session_id (FK)─│─────────────────────────────┘
        │             │   │ level           │
        │             │   │ role            │
        │             │   │ content         │
        │             │   │ timestamp       │
        │             │   │ attack_type     │
        │             │   │ leaked_info     │
        │             │   └─────────────────┘
        │             │
        ▼             │
┌─────────────────┐   │   ┌─────────────────┐
│   leaderboard   │   │   │  level_secrets  │
├─────────────────┤   │   ├─────────────────┤
│ id (PK)         │   │   │ id (PK)         │
│ user_id (FK)────│───┘   │ level (UNIQUE)  │
│ username        │       │ secret          │
│ level           │       │ passphrase      │
│ attempts        │       │ description     │
│ time_seconds    │       │ created_at      │
│ completed_at    │       │ updated_at      │
└─────────────────┘       └─────────────────┘
```

## Tables

### users

Stores registered user accounts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique user identifier |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL, INDEXED | User's display name |
| `email` | VARCHAR(100) | UNIQUE, NULLABLE | User's email address |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt-hashed password |
| `created_at` | DATETIME | DEFAULT NOW | Account creation timestamp |

**Relationships:**
- One-to-Many → `game_sessions`
- One-to-Many → `leaderboard`

---

### game_sessions

Tracks individual game play sessions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique session identifier |
| `user_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | Owner of the session |
| `session_token` | VARCHAR(64) | UNIQUE, NOT NULL, INDEXED | API session token |
| `current_level` | INTEGER | DEFAULT 1 | Current level being played |
| `started_at` | DATETIME | DEFAULT NOW | Session start time |
| `last_activity` | DATETIME | DEFAULT NOW, ON UPDATE | Last activity timestamp |
| `is_active` | BOOLEAN | DEFAULT TRUE | Whether session is active |

**Relationships:**
- Many-to-One → `users`
- One-to-Many → `level_attempts`
- One-to-Many → `chat_messages`

---

### level_attempts

Tracks progress and statistics for each level attempt.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique attempt identifier |
| `session_id` | INTEGER | FOREIGN KEY → game_sessions.id, NOT NULL | Parent session |
| `level` | INTEGER | NOT NULL | Level number (1-5) |
| `attempts` | INTEGER | DEFAULT 0 | Number of passphrase attempts |
| `messages_sent` | INTEGER | DEFAULT 0 | Number of chat messages sent |
| `completed` | BOOLEAN | DEFAULT FALSE | Whether level was completed |
| `completed_at` | DATETIME | NULLABLE | Completion timestamp |
| `time_spent_seconds` | FLOAT | DEFAULT 0.0 | Time to complete in seconds |
| `started_at` | DATETIME | DEFAULT NOW | Attempt start time |

**Relationships:**
- Many-to-One → `game_sessions`

---

### chat_messages

Stores all chat interactions for history and analysis.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique message identifier |
| `session_id` | INTEGER | FOREIGN KEY → game_sessions.id, NOT NULL | Parent session |
| `level` | INTEGER | NOT NULL | Level number (1-5) |
| `role` | VARCHAR(20) | NOT NULL | Message author: `user` or `assistant` |
| `content` | TEXT | NOT NULL | Message content |
| `timestamp` | DATETIME | DEFAULT NOW | Message timestamp |
| `attack_type` | VARCHAR(50) | NULLABLE | Detected attack pattern (for analysis) |
| `leaked_info` | BOOLEAN | DEFAULT FALSE | Whether secret was leaked |

**Relationships:**
- Many-to-One → `game_sessions`

---

### leaderboard

Stores completion records for ranking players.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique entry identifier |
| `user_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | User who completed |
| `username` | VARCHAR(50) | NOT NULL | Username at time of completion |
| `level` | INTEGER | NOT NULL | Completed level number |
| `attempts` | INTEGER | NOT NULL | Number of attempts to complete |
| `time_seconds` | FLOAT | NOT NULL | Time to complete in seconds |
| `completed_at` | DATETIME | DEFAULT NOW | Completion timestamp |

**Relationships:**
- Many-to-One → `users`

---

### level_secrets

Admin-configurable secrets for each level.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique secret identifier |
| `level` | INTEGER | UNIQUE, NOT NULL | Level number (1-5) |
| `secret` | VARCHAR(255) | NOT NULL | The secret to protect |
| `passphrase` | VARCHAR(100) | NOT NULL | Passphrase that unlocks the secret |
| `description` | TEXT | NULLABLE | Description of the level secret |
| `created_at` | DATETIME | DEFAULT NOW | Creation timestamp |
| `updated_at` | DATETIME | DEFAULT NOW, ON UPDATE | Last update timestamp |

---

## Indexes

| Table | Index Name | Columns | Type |
|-------|------------|---------|------|
| users | `ix_users_username` | username | UNIQUE |
| users | `ix_users_email` | email | UNIQUE |
| game_sessions | `ix_game_sessions_session_token` | session_token | UNIQUE |

## Migrations

Database migrations are managed with Alembic. Migration files are located in `alembic/versions/`.

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"

# Rollback one migration
alembic downgrade -1
```
