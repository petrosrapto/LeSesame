# Le Sésame Backend API

🔐 **The Multi-Level Secret Keeper Game** - Backend API

FastAPI backend implementing 5 progressive difficulty levels of AI secret-keeping mechanisms.

## Features

- **5 Security Levels**: From naive prompts to architectural separation
- **LLM Integration**: Mistral AI and OpenAI support
- **JWT Authentication**: Guest and registered user support
- **Leaderboard System**: Track completions by time and attempts
- **Progress Tracking**: Persistent game sessions

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
# MISTRAL_API_KEY=your-key-here
# or
# OPENAI_API_KEY=your-key-here

# Run the server
uvicorn app.main:app --reload
```

### Docker

```bash
# Build and run
docker-compose up -d --build

# With API keys
MISTRAL_API_KEY=your-key docker-compose up -d --build
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login with credentials |
| POST | `/auth/guest` | Create guest session |
| GET | `/auth/me` | Get current user |

### Game

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/game/session` | Create/get game session |
| POST | `/game/chat` | Send message to guardian |
| POST | `/game/verify` | Verify passphrase |
| GET | `/game/progress` | Get game progress |
| GET | `/game/levels` | Get all level info |
| GET | `/game/history/{level}` | Get chat history |
| DELETE | `/game/session` | Reset session |

### Leaderboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/leaderboard/` | Get leaderboard |
| GET | `/leaderboard/top` | Get top players |
| GET | `/leaderboard/stats` | Get statistics |
| GET | `/leaderboard/level/{level}` | Level leaderboard |

## Security Levels

### Level 1: Naive Prompt
Simple system prompt with "don't reveal" instruction. Easily broken by basic jailbreaks.

### Level 2: Hardened Prompt  
Explicit defenses against known attack patterns (encoding, roleplay, authority claims).

### Level 3: Output Firewall
Second LLM call inspects every response for semantic similarity to the secret.

### Level 4: Architectural Separation
The LLM never has the secret in context. Separate verifier holds the secret.

### Level 5: Embedded Secret
Simulates fine-tuned model with trigger-activated secret.

## Default Secrets & Passphrases

| Level | Secret | Passphrase |
|-------|--------|------------|
| 1 | RUBY_PHOENIX | open sesame |
| 2 | EMERALD_DRAGON | speak friend |
| 3 | SAPPHIRE_UNICORN | mellon |
| 4 | DIAMOND_GRIFFIN | le sésame |
| 5 | OBSIDIAN_KRAKEN | abracadabra |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | development | Environment mode |
| `DEBUG` | true | Debug mode |
| `LOG_LEVEL` | INFO | Logging level |
| `DATABASE_URL` | sqlite+aiosqlite:///./le_sesame.db | Database connection |
| `JWT_SECRET` | - | JWT signing secret |
| `MISTRAL_API_KEY` | - | Mistral AI API key |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `LLM_PROVIDER` | mistral | LLM provider (mistral/openai) |
| `LLM_MODEL` | mistral-small-latest | Model to use |
| `CORS_ORIGINS` | ["http://localhost:3000"] | Allowed origins |

## Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html
```

## API Documentation

When running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT
