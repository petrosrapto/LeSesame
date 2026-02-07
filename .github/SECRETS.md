# GitHub Secrets Configuration for Le Sésame CI/CD

This document lists all the GitHub secrets required for the CI/CD pipeline to work correctly.

## How to Configure

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Create a new environment called `dev`
4. Add the secrets listed below

## Required Secrets

### Infrastructure / VPN Secrets

| Secret Name | Description | Example |
|------------|-------------|---------|
| `VPN_PRIVATE_KEY` | VPN private key for connecting to the server | PEM format private key |
| `OPENVPN_CONFIG` | OpenVPN configuration file contents | `.ovpn` file contents |
| `REMOTE_SERVER_IP` | IP address of the deployment server | `10.0.0.100` |
| `SSH_USER` | SSH username for the deployment server | `deploy` |
| `SSH_PRIVATE_KEY_B64` | Base64-encoded SSH private key | `base64 -i id_rsa` |
| `GHCR_PAT` | GitHub Container Registry Personal Access Token | `ghp_xxxx` |

### Database Secrets

| Secret Name | Description | Default Value |
|------------|-------------|---------------|
| `POSTGRES_DB` | PostgreSQL database name | `le_sesame` |
| `POSTGRES_USER` | PostgreSQL username | `le_sesame_user` |
| `POSTGRES_PASSWORD` | PostgreSQL password | _(set a strong password)_ |
| `DATABASE_URL` | Full PostgreSQL connection URL | `postgresql+asyncpg://le_sesame_user:PASSWORD@postgres:5432/le_sesame` |

### Backend Application Secrets

| Secret Name | Description | Default Value |
|------------|-------------|---------------|
| `ENVIRONMENT` | Environment name | `production` |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `JWT_SECRET` | **REQUIRED** - JWT signing secret | _(generate a strong secret)_ |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRATION_HOURS` | Token expiration in hours | `24` |
| `MISTRAL_API_KEY` | Mistral AI API key | _(optional)_ |
| `OPENAI_API_KEY` | OpenAI API key | _(optional)_ |
| `LLM_PROVIDER` | LLM provider to use | `mistral` |
| `LLM_MODEL` | LLM model name | `mistral-small-latest` |
| `DEFAULT_SECRET` | Default game secret | `GOLDEN_KEY_2024` |
| `DEFAULT_PASSPHRASE` | Default passphrase | `open sesame` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `CORS_ORIGINS` | CORS allowed origins | `["http://frontend:3000","http://localhost:3000"]` |

### Frontend Application Secrets

| Secret Name | Description | Default Value |
|------------|-------------|---------------|
| `VITE_API_URL` | Backend API URL | `http://backend:8000` |
| `VITE_ENABLE_AUTH` | Enable authentication | `true` |
| `NODE_ENV` | Node environment | `production` |

## Generating Required Values

### Generate a JWT Secret
```bash
openssl rand -hex 32
```

### Base64 Encode SSH Private Key
```bash
base64 -i ~/.ssh/id_rsa
```

### Generate a Strong Password
```bash
openssl rand -base64 24
```

## Pipeline Overview

The CI/CD pipeline performs the following:

1. **CI Jobs** (on every push/PR):
   - Frontend build & lint
   - Frontend unit tests
   - Backend unit tests

2. **Build & Push** (on main/master):
   - Build Docker images
   - Push to GitHub Container Registry (ghcr.io)

3. **Deploy** (on main/master):
   - Connect to VPN
   - SSH to remote server
   - Copy `docker-compose.yml` and config files from `deployment/dev/`
   - Create `.env` files from secrets
   - Pull and deploy containers

## Files Used in Deployment

The pipeline reads these files from the `deployment/dev/` directory:

- `deployment/dev/docker-compose.yml` - Docker Compose configuration
- `deployment/dev/backend/config.dev.yaml` - Backend YAML configuration
- `deployment/dev/backend/.env.example` - Reference for backend env vars
- `deployment/dev/frontend/.env.example` - Reference for frontend env vars
