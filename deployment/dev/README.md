# Dev Environment Deployment

This directory contains configuration for CI/CD deployment to the development/staging environment.

## Directory Structure

```
dev/
├── docker-compose.yml     # Full stack compose (pre-built images)
├── backend/
│   ├── .env.example       # Template for environment variables
│   ├── .env               # Environment variables (server-side only)
│   └── config.dev.yaml    # Backend YAML configuration
├── frontend/
│   ├── .env.example       # Template for environment variables
│   └── .env               # Environment variables (server-side only)
├── scripts/
│   ├── deploy.sh          # Deployment script for remote server
│   └── cleanup.sh         # Cleanup script for remote server
└── README.md              # This file
```

## CI/CD Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        CI/CD Pipeline                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────────┐    ┌────────────────┐  │
│  │  Test Stage │ -> │   Build Stage   │ -> │  Deploy Stage  │  │
│  │             │    │                 │    │                │  │
│  │ - Unit tests│    │ - Build images  │    │ - SSH to server│  │
│  │ - Linting   │    │ - Push to       │    │ - Pull images  │  │
│  │             │    │   Registry      │    │ - Start svcs   │  │
│  └─────────────┘    └─────────────────┘    └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Required Environment Variables

### Backend
```bash
# Docker image (set by CI)
BACKEND_IMAGE=registry.example.com/le-sesame/backend:sha

# Security
JWT_SECRET=your-production-secret-here

# LLM Configuration (at least one required for real responses)
MISTRAL_API_KEY=your-mistral-api-key
OPENAI_API_KEY=your-openai-api-key
LLM_PROVIDER=mistral
LLM_MODEL=mistral-small-latest
```

### Frontend
```bash
# Docker image (set by CI)
FRONTEND_IMAGE=registry.example.com/le-sesame/frontend:sha

# API Configuration
VITE_API_URL=http://backend:8000
VITE_ENABLE_AUTH=true
```

## Manual Deployment

If deploying manually (not via CI/CD):

```bash
# 1. SSH to the server
ssh user@server

# 2. Navigate to deployment directory
cd ~/le-sesame-deploy/dev

# 3. Create .env files with required variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit the .env files with your values

# 4. Run deployment script
./scripts/deploy.sh
```

## Health Checks

Both services include health check endpoints:

- **Backend**: `GET /health`
- **Frontend**: `GET /` (page load test)

## Accessing the Application

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://server:3000 | Main application |
| Backend | http://server:8000 | API server |
| API Docs | http://server:8000/docs | OpenAPI documentation |

## Cleanup

```bash
# Stop all services
./scripts/cleanup.sh

# Or manually
docker-compose down -v
```
