# GitHub Secrets Configuration for Le Sésame CI/CD

This document lists all the GitHub secrets required for the CI/CD pipeline to work correctly.

## How to Configure

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Create a new environment called `dev`
4. Add the secrets listed below

> **How `.env` generation works:** The pipeline reads each `.env.example` file from `deployment/dev/`, and for every `KEY=value` line:
> - If a GitHub secret with the same name is set → uses the secret value
> - If the value is a non-placeholder default (e.g. `HOST=0.0.0.0`) → keeps it as-is
> - If the value is a placeholder (`<...>`) and no secret is set → skips it
>
> To add a new variable: add it to the appropriate `.env.example`, set the secret in GitHub, and add one `VAR: ${{ secrets.VAR }}` line in the CI workflow's `env:` block.

## Required Secrets

### Infrastructure / VPN / SSH Secrets

| Secret Name | Description | Required | Example |
|------------|-------------|----------|---------|
| `VPN_PRIVATE_KEY` | VPN private key for connecting to the server | Yes | PEM format private key |
| `OPENVPN_CONFIG` | OpenVPN configuration file contents | Yes | `.ovpn` file contents |
| `REMOTE_SERVER_IP` | IP address of the deployment server | Yes | `10.0.0.100` |
| `SSH_USER` | SSH username for the deployment server | Yes | `deploy` |
| `SSH_PRIVATE_KEY_B64` | Base64-encoded SSH private key | Yes | `base64 -i id_rsa` |
| `GHCR_PAT` | GitHub Container Registry Personal Access Token | Yes | `ghp_xxxx` |

### Database Secrets

| Secret Name | Description | Required | Default if unset |
|------------|-------------|----------|------------------|
| `POSTGRES_DB` | PostgreSQL database name | Yes | — |
| `POSTGRES_USER` | PostgreSQL username | Yes | — |
| `POSTGRES_PASSWORD` | PostgreSQL password | Yes | — |

### Backend — Environment & Server

| Secret Name | Description | Required | Default if unset |
|------------|-------------|----------|------------------|
| `ENVIRONMENT` | Environment name (`production`, `staging`, etc.) | No | _(skipped — placeholder)_ |
| `DEBUG` | Debug mode (`true`/`false`) | No | _(skipped — placeholder)_ |
| `LOG_LEVEL` | Logging level (`INFO`, `WARNING`, etc.) | No | _(skipped — placeholder)_ |
| `HOST` | Server bind host | No | `0.0.0.0` (from `.env.example`) |
| `PORT` | Server bind port | No | `8000` (from `.env.example`) |

### Backend — JWT Authentication

| Secret Name | Description | Required | Default if unset |
|------------|-------------|----------|------------------|
| `JWT_SECRET` | **REQUIRED** — JWT signing secret | Yes | CI tests fallback: `test-secret-key-for-ci` |
| `JWT_ALGORITHM` | JWT algorithm | No | CI tests fallback: `HS256` |
| `JWT_EXPIRATION_HOURS` | Token expiration in hours | No | CI tests fallback: `24` |

### Backend — LLM API Keys

All optional — set only the ones you use. Variables without a secret are skipped (placeholder values in `.env.example`).

| Secret Name | Description |
|------------|-------------|
| `MISTRAL_API_KEY` | Mistral AI API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `GOOGLE_API_KEY` | Google AI API key |
| `ALIBABA_API_KEY` | Alibaba / DashScope API key |
| `DEEPSEEK_API_KEY` | DeepSeek API key |
| `VLLM_API_KEY` | vLLM endpoint API key |
| `TOGETHER_API_KEY` | Together AI API key |
| `OPENAI_ENDPOINT_URL` | Custom OpenAI-compatible endpoint URL |

### Backend — AWS Bedrock

| Secret Name | Description | Required |
|------------|-------------|----------|
| `AWS_ACCESS_KEY_ID` | AWS access key ID | No |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | No |
| `AWS_REGION_NAME` | AWS region (e.g. `us-east-1`) | No |

### Backend — LangSmith Tracing

| Secret Name | Description | Required |
|------------|-------------|----------|
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing (`true`/`false`) | No |
| `LANGCHAIN_PROJECT` | LangSmith project name | No |
| `LANGCHAIN_API_KEY` | LangSmith API key | No |
| `LANGCHAIN_ENDPOINT` | LangSmith endpoint URL | No |

### Frontend Application Secrets

| Secret Name | Description | Required | Default if unset |
|------------|-------------|----------|------------------|
| `VITE_API_URL` | Backend API URL | No | `http://backend:8000` (from `.env.example`) |
| `VITE_ENABLE_AUTH` | Enable authentication | No | `true` (from `.env.example`) |
| `NODE_ENV` | Node environment | No | `production` (from `.env.example`) |

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
   - Frontend unit tests with coverage
   - Backend unit tests with coverage (`.env` generated from `deployment/dev/backend/.env.example`)

2. **Build & Push** (on main/master, currently disabled):
   - Build Docker images
   - Push to GitHub Container Registry (ghcr.io)

3. **Deploy** (on main/master, currently disabled):
   - Connect to VPN
   - SSH to remote server
   - Generate `.env` files from `deployment/dev/*.env.example` + GitHub secrets
   - Copy entire `deployment/dev/` directory to remote (including generated `.env` files)
   - Run `scripts/deploy.sh` (handles image pull, service start, and health checks)
   - Verify with `scripts/deploy.sh --status`

## Files Used in Deployment

The pipeline reads these files from the `deployment/dev/` directory:

| File | Purpose |
|------|---------|
| `deployment/dev/.env.example` | Root docker-compose variables (`POSTGRES_*`, `*_IMAGE`) |
| `deployment/dev/backend/.env.example` | Backend environment variables template |
| `deployment/dev/frontend/.env.example` | Frontend environment variables template |
| `deployment/dev/docker-compose.yml` | Docker Compose service configuration |
| `deployment/dev/backend/config.dev.yaml` | Backend YAML config (game levels, LLM, CORS) |
| `deployment/dev/scripts/deploy.sh` | Deployment script (pull, start, health checks) |
| `deployment/dev/scripts/cleanup.sh` | Cleanup script (stop, remove containers) |
