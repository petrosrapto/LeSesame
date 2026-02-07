# Le Sésame 🔐

**Multi-Level Secret Keeper Game** — A Mistral AI Moonshot Challenge

> Can we design an AI system that preserves information asymmetry—internally retaining a secret, demonstrating knowledge of it when required, revealing it only under authorized conditions, and remaining robust against adversarial extraction attempts?

## 🎮 The Game

Le Sésame is an interactive game where players attempt to extract secrets from AI guardians. Each level implements progressively more sophisticated secret-keeping mechanisms, challenging players to find creative ways to break through the defenses.

### Levels

| Level | Name | Difficulty | Security Mechanism |
|-------|------|------------|-------------------|
| 1 | **Le Naïf** | Easy | Basic system prompt instruction |
| 2 | **Le Gardien** | Medium | Hardened prompt with explicit defenses |
| 3 | **Le Vigilant** | Hard | Output firewall with semantic analysis |
| 4 | **L'Architecte** | Expert | Architectural separation (secret held externally) |
| 5 | **Le Cryptique** | Master | Fine-tuned weights with trigger activation |

### How to Play

1. Chat with the AI guardian at your current level
2. Try to extract the secret using any technique you can think of
3. When you think you know the passphrase, submit it for verification
4. If correct, you unlock the secret and advance to the next level

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│   PostgreSQL    │
│   (Next.js)     │     │   (FastAPI)     │     │   (Database)    │
│   Port: 3000    │     │   Port: 8000    │     │   Port: 5432    │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   LLM Provider  │
                        │ (Mistral/OpenAI)│
                        └─────────────────┘
```

### Tech Stack

- **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS, Zustand
- **Backend:** FastAPI, Python 3.11, SQLAlchemy 2.0 (async), Pydantic
- **Database:** PostgreSQL 15 with asyncpg
- **LLM:** Mistral AI / OpenAI (configurable)
- **Infrastructure:** Docker, Docker Compose, GitHub Actions CI/CD

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Run with Docker Compose (Recommended)

```bash
# Navigate to the local deployment directory
cd deployment/local

# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f
```

Access the application:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Run Locally (Development)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL (or use Docker)
docker run -d --name postgres -e POSTGRES_USER=le_sesame_user -e POSTGRES_PASSWORD=le_sesame_password -e POSTGRES_DB=le_sesame -p 5432:5432 postgres:15-alpine

# Run the backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pip install -r requirements-test.txt
pytest tests/ -v --cov=app
```

**Test Coverage:** 33 tests covering:
- Health endpoints
- Authentication (registration, login, token validation)
- Game logic (levels, sessions, chat, progress)
- Pydantic schema validation

### Frontend Tests

```bash
cd frontend
npm run test
```

**Test Coverage:** 46 tests covering:
- React components
- Custom hooks
- API utilities
- Constants and configuration

### Run All Tests with Coverage

```bash
# Backend
cd backend && pytest tests/ --cov=app --cov-report=html

# Frontend
cd frontend && npm run test:ci
```

---

## 📁 Project Structure

```
.
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic (LLM, levels)
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database setup
│   │   ├── models.py          # SQLAlchemy models
│   │   └── schemas.py         # Pydantic schemas
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Unit tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # App router pages
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   └── lib/               # Utilities
│   ├── Dockerfile
│   └── package.json
│
├── deployment/                 # Deployment configurations
│   ├── local/                 # Local development
│   │   ├── docker-compose.yml
│   │   ├── backend/           # Backend config & env
│   │   └── frontend/          # Frontend env
│   └── dev/                   # Dev/staging deployment
│       ├── docker-compose.yml
│       ├── backend/           # Backend config & env
│       └── frontend/          # Frontend env
│
└── .github/
    ├── workflows/ci.yml       # CI/CD pipeline
    └── SECRETS.md             # Required GitHub secrets
```

---

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline includes:

### CI (on every push/PR)
- ✅ Frontend lint & build
- ✅ Frontend unit tests with coverage
- ✅ Backend unit tests with coverage

### CD (on main/master)
- 🐳 Build Docker images
- 📦 Push to GitHub Container Registry
- 🚀 Deploy to remote server via VPN

See [.github/SECRETS.md](.github/SECRETS.md) for required GitHub secrets configuration.

---

## 🎯 Problem Reframing

**Original Challenge:** "Design an AI that can keep a secret."

**The Analogy:** This is essentially **symmetric encryption implemented in natural language**. The secret is the plaintext, the passphrase is the shared key, and the LLM system is the encryption/decryption mechanism.

**Requirements:**
- **Prove** it knows the secret (output it when given the correct passphrase)
- **Resist** revealing it under all other conditions (adversarial robustness)

### Attack Categories Defended Against

- Direct extraction (asking for the secret)
- Authority claims (pretending to be a developer)
- Jailbreaks (DAN-style prompts)
- Encoding attacks (backwards, Base64, first letters)
- Roleplay / context switching
- Multi-turn deduction (aggregating partial information)
- Prompt dumping (extracting system instructions)
- Translation attacks

---

## 🔮 Future Enhancements

- **Red Team Attack Suite:** Automated adversarial testing
- **Leaderboard:** Track secrecy rates and player rankings
- **User-submitted Defenses:** Upload custom prompts/LoRA adapters
- **Enterprise Scenarios:** Role-based access with realistic data
- **Adaptive Red Team:** LLM-powered attacker that learns

---

## 👤 Author

**Petros Raptopoulos**

Mistral AI Moonshot Challenge, February 2025

---

## 📄 License

This project is proprietary and was created for the Mistral AI interview process.
