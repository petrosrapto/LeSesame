#!/bin/bash
# Le Sésame - Local Development Deployment Script
#
# This script handles the complete local deployment of the Le Sésame application:
# - Validates configuration files and environment
# - Stops existing containers
# - Builds Docker images from source
# - Starts all services with health checks
#
# Usage:
#   ./deploy.sh              # Build and deploy all services
#   ./deploy.sh --down       # Stop and remove all containers
#   ./deploy.sh --restart    # Restart all services
#   ./deploy.sh --status     # Show status of all services
#   ./deploy.sh --logs       # Show logs from all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$DEPLOY_DIR")")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
COMPOSE_FILE="$DEPLOY_DIR/docker-compose.yml"

# Parse arguments
STOP_ONLY=false
RESTART=false
SHOW_STATUS=false
SHOW_LOGS=false

for arg in "$@"; do
    case $arg in
        --down|-d)
            STOP_ONLY=true
            shift
            ;;
        --restart|-r)
            RESTART=true
            shift
            ;;
        --status|-s)
            SHOW_STATUS=true
            shift
            ;;
        --logs|-l)
            SHOW_LOGS=true
            shift
            ;;
        --help|-h)
            echo "Le Sésame - Local Deployment Script"
            echo ""
            echo "Usage: ./deploy.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --down, -d      Stop and remove all containers"
            echo "  --restart, -r   Restart all services"
            echo "  --status, -s    Show status of all services"
            echo "  --logs, -l      Show logs from all services"
            echo "  --help, -h      Show this help message"
            exit 0
            ;;
    esac
done

echo -e "${YELLOW}============================================${NC}"
echo -e "${YELLOW}  Le Sésame - Local Development Deployment${NC}"
echo -e "${YELLOW}============================================${NC}"
echo ""
echo -e "Project Root:  ${BLUE}$PROJECT_ROOT${NC}"
echo -e "Deploy Dir:    ${BLUE}$DEPLOY_DIR${NC}"
echo ""

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running!${NC}"
        echo "   Please start Docker Desktop and try again."
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is running${NC}"
}

# Function to stop all containers
stop_containers() {
    echo -e "\n${YELLOW}📦 Stopping existing containers...${NC}"
    cd "$DEPLOY_DIR"
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true

    # Also stop any conflicting containers by name
    for container in le-sesame-postgres le-sesame-backend le-sesame-frontend; do
        if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
            echo -e "   Removing conflicting container: ${container}"
            docker rm -f "$container" 2>/dev/null || true
        fi
    done

    echo -e "${GREEN}✅ Containers stopped${NC}"
}

# Function to show status
show_status() {
    echo -e "\n${YELLOW}📊 Container Status:${NC}"
    cd "$DEPLOY_DIR"
    docker-compose -f "$COMPOSE_FILE" ps
}

# Function to show logs
show_logs() {
    echo -e "\n${YELLOW}📜 Container Logs:${NC}"
    cd "$DEPLOY_DIR"
    docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
}

# Handle special modes
if [ "$SHOW_STATUS" = true ]; then
    check_docker
    show_status
    exit 0
fi

if [ "$SHOW_LOGS" = true ]; then
    check_docker
    show_logs
    exit 0
fi

if [ "$STOP_ONLY" = true ]; then
    check_docker
    stop_containers
    echo -e "\n${GREEN}✅ All containers stopped${NC}"
    exit 0
fi

if [ "$RESTART" = true ]; then
    check_docker
    stop_containers
    echo -e "\n${YELLOW}🔄 Restarting services...${NC}"
    cd "$DEPLOY_DIR"
    docker-compose -f "$COMPOSE_FILE" up -d
    show_status
    exit 0
fi

# Main deployment flow
check_docker

# ============================================
# Step 1: Validate Configuration Files
# ============================================
echo -e "\n${YELLOW}📋 Step 1: Validating configuration files...${NC}"

ERRORS=0

# Check docker-compose.yml exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ docker-compose.yml not found at $COMPOSE_FILE${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ docker-compose.yml found${NC}"
fi

# Check backend .env (auto-copy from .env.example if missing)
if [ ! -f "$DEPLOY_DIR/backend/.env" ]; then
    if [ -f "$DEPLOY_DIR/backend/.env.example" ]; then
        echo -e "${YELLOW}⚠️  Backend .env not found, copying from .env.example...${NC}"
        cp "$DEPLOY_DIR/backend/.env.example" "$DEPLOY_DIR/backend/.env"
    else
        echo -e "${RED}❌ Backend .env and .env.example not found!${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${GREEN}✅ Backend .env found${NC}"
fi

# Check frontend .env (auto-copy from .env.example if missing)
if [ ! -f "$DEPLOY_DIR/frontend/.env" ]; then
    if [ -f "$DEPLOY_DIR/frontend/.env.example" ]; then
        echo -e "${YELLOW}⚠️  Frontend .env not found, copying from .env.example...${NC}"
        cp "$DEPLOY_DIR/frontend/.env.example" "$DEPLOY_DIR/frontend/.env"
    else
        echo -e "${RED}❌ Frontend .env and .env.example not found!${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${GREEN}✅ Frontend .env found${NC}"
fi

# Check backend config file
if [ ! -f "$DEPLOY_DIR/backend/config.local.yaml" ]; then
    echo -e "${YELLOW}⚠️  Backend config.local.yaml not found (optional)${NC}"
else
    echo -e "${GREEN}✅ Backend config.local.yaml found${NC}"
fi

# Check source directories and Dockerfiles
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend source directory not found: $BACKEND_DIR${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Backend source directory found${NC}"
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend source directory not found: $FRONTEND_DIR${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Frontend source directory found${NC}"
fi

if [ ! -f "$BACKEND_DIR/Dockerfile" ]; then
    echo -e "${RED}❌ Backend Dockerfile not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

if [ ! -f "$FRONTEND_DIR/Dockerfile" ]; then
    echo -e "${RED}❌ Frontend Dockerfile not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Exit if there are errors
if [ $ERRORS -gt 0 ]; then
    echo -e "\n${RED}❌ Found $ERRORS configuration error(s). Please fix them and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All configuration files validated${NC}"

# ============================================
# Step 2: Stop Existing Containers
# ============================================
stop_containers

# ============================================
# Step 3: Build and Start Services
# ============================================
echo -e "\n${YELLOW}🏗️  Step 3: Building and starting services from source...${NC}"

# Export NEXT_PUBLIC_* variables from frontend/.env so docker-compose
# can pass them as build args (they must be set at build time for Next.js).
if [ -f "$DEPLOY_DIR/frontend/.env" ]; then
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ -z "$key" || "$key" == \#* ]] && continue
        # Only export NEXT_PUBLIC_ variables
        if [[ "$key" == NEXT_PUBLIC_* ]]; then
            export "${key}=${value}"
        fi
    done < "$DEPLOY_DIR/frontend/.env"
    echo -e "${GREEN}✅ Exported NEXT_PUBLIC_* build args from frontend/.env${NC}"
fi

cd "$DEPLOY_DIR"
docker-compose -f "$COMPOSE_FILE" up -d --build

echo -e "${GREEN}✅ Services built and started${NC}"

# ============================================
# Step 4: Health Checks
# ============================================
echo -e "\n${YELLOW}🏥 Step 4: Running health checks...${NC}"

# Load DB credentials from backend .env (with defaults matching docker-compose.yml)
if [ -f "$DEPLOY_DIR/backend/.env" ]; then
    POSTGRES_USER=$(grep -E '^POSTGRES_USER=' "$DEPLOY_DIR/backend/.env" | cut -d '=' -f2- | tr -d '[:space:]')
    POSTGRES_DB=$(grep -E '^POSTGRES_DB=' "$DEPLOY_DIR/backend/.env" | cut -d '=' -f2- | tr -d '[:space:]')
fi
POSTGRES_USER="${POSTGRES_USER:-le_sesame_user}"
POSTGRES_DB="${POSTGRES_DB:-le_sesame}"

# Wait for PostgreSQL
echo -e "\n${BLUE}Checking PostgreSQL...${NC}"
for i in {1..30}; do
    if docker exec le-sesame-postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ PostgreSQL health check timeout${NC}"
        docker logs le-sesame-postgres --tail=20
        exit 1
    fi
    echo -n "."
    sleep 1
done

# Wait for Backend
echo -e "\n${BLUE}Checking Backend API...${NC}"
for i in {1..60}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        HEALTH=$(curl -s http://localhost:8000/health)
        echo -e "${GREEN}✅ Backend is healthy${NC}"
        echo -e "   Response: $HEALTH"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}❌ Backend health check timeout${NC}"
        echo "Backend logs:"
        docker logs le-sesame-backend --tail=30
        exit 1
    fi
    echo -n "."
    sleep 2
done

# Wait for Frontend
echo -e "\n${BLUE}Checking Frontend...${NC}"
for i in {1..60}; do
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is ready${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${YELLOW}⚠️  Frontend health check timeout (may still be starting)${NC}"
    fi
    echo -n "."
    sleep 2
done

# ============================================
# Deployment Complete
# ============================================
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  ✅ Deployment Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "🌐 Frontend:   ${BLUE}http://localhost:3000${NC}"
echo -e "🔧 Backend:    ${BLUE}http://localhost:8000${NC}"
echo -e "📚 API Docs:   ${BLUE}http://localhost:8000/docs${NC}"
echo -e "🗄️  Database:   ${BLUE}localhost:5432${NC}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  View logs:     ${BLUE}./deploy.sh --logs${NC}"
echo -e "  Stop services: ${BLUE}./deploy.sh --down${NC}"
echo -e "  Restart:       ${BLUE}./deploy.sh --restart${NC}"
echo -e "  Status:        ${BLUE}./deploy.sh --status${NC}"
echo -e "  Cleanup:       ${BLUE}$SCRIPT_DIR/cleanup.sh${NC}"
echo ""

# Show container status
show_status
