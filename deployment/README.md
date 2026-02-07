# Le Sésame - Deployment Configurations

This directory contains deployment configurations for different environments.

## Directory Structure

```
deployment/
├── local/                  # Local development environment
│   ├── docker-compose.yml  # Full stack compose (builds from source)
│   ├── backend/            # Backend .env and config.yaml
│   ├── frontend/           # Frontend .env
│   ├── scripts/            # deploy.sh, cleanup.sh
│   └── README.md
├── dev/                    # Dev/staging environment  
│   ├── docker-compose.yml  # Full stack compose (pre-built images)
│   ├── backend/            # Backend .env and config.yaml
│   ├── frontend/           # Frontend .env
│   ├── scripts/            # deploy.sh, cleanup.sh
│   └── README.md
└── README.md               # This file
```

## Environments

### Local (`local/`)
- For local development on developer machines
- Uses `docker-compose build` to build images locally
- PostgreSQL database (same as production)
- Default secrets for easy testing

### Dev (`dev/`)
- For CI/CD deployment to development/staging servers
- Uses pre-built images from container registry
- More production-like configuration
- Requires proper environment variables

## Quick Start

### Local Development
```bash
cd deployment/local
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker-compose up -d --build
```

### Dev Deployment
```bash
cd deployment/dev
# Set environment variables in .env files
./scripts/deploy.sh
```

## Service URLs

| Environment | Frontend | Backend | API Docs |
|-------------|----------|---------|----------|
| Local | http://localhost:3000 | http://localhost:8000 | http://localhost:8000/docs |
| Dev | http://server:3000 | http://server:8000 | http://server:8000/docs |
