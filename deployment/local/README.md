# Local Development Deployment

This directory contains configuration for local development using Docker.

## Directory Structure

```
local/
├── docker-compose.yml     # Full stack compose (backend + frontend)
├── backend/
│   ├── .env.example       # Template for environment variables
│   ├── .env               # Your local environment variables (git-ignored)
│   └── config.local.yaml  # Backend YAML configuration
├── frontend/
│   ├── .env.example       # Template for environment variables
│   └── .env               # Your local environment variables (git-ignored)
├── scripts/
│   ├── deploy.sh          # Start all services
│   └── cleanup.sh         # Stop and cleanup
└── README.md              # This file
```

## Quick Start

### 1. Configure Environment

```bash
# Copy example env files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit .env files with your API keys (optional for mock mode)
```

### 2. Start All Services

```bash
# Using docker-compose directly
docker-compose up -d --build

# Or using the deploy script
./scripts/deploy.sh
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Individual Service Commands

### Backend Only
```bash
docker-compose up -d --build backend
```

### Frontend Only
```bash
docker-compose up -d --build frontend
```

## Environment Variables

### Backend (.env)
| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET` | Secret for JWT signing | `dev-secret-change-me` |
| `MISTRAL_API_KEY` | Mistral AI API key | (empty = mock mode) |
| `OPENAI_API_KEY` | OpenAI API key | (empty = mock mode) |
| `LLM_PROVIDER` | Which LLM to use | `mistral` |
| `LLM_MODEL` | Model identifier | `mistral-small-latest` |

### Frontend (.env)
| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_ENABLE_AUTH` | Enable authentication | `true` |

## Cleanup

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (database data)
docker-compose down -v

# Or use the cleanup script
./scripts/cleanup.sh
```
