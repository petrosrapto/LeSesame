#!/bin/bash
# Le Sésame - Dev Environment Cleanup Script
# Stops and removes all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$DEPLOY_DIR/docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}============================================${NC}"
echo -e "${YELLOW}  Le Sésame - Dev Cleanup${NC}"
echo -e "${YELLOW}============================================${NC}"
echo ""

# Parse arguments
REMOVE_VOLUMES=false
REMOVE_IMAGES=false
for arg in "$@"; do
    case $arg in
        -v|--volumes)
            REMOVE_VOLUMES=true
            shift
            ;;
        -i|--images)
            REMOVE_IMAGES=true
            shift
            ;;
        -a|--all)
            REMOVE_VOLUMES=true
            REMOVE_IMAGES=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -v, --volumes    Also remove volumes (database data will be lost)"
            echo "  -i, --images     Also remove pulled/built images"
            echo "  -a, --all        Remove volumes and images"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
    esac
done

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

cd "$DEPLOY_DIR"

echo -e "${YELLOW}🛑 Stopping services...${NC}"
if [ "$REMOVE_VOLUMES" = true ]; then
    echo -e "${RED}⚠️  Also removing volumes (database data will be lost)${NC}"
    docker compose -f "$COMPOSE_FILE" down -v --remove-orphans 2>/dev/null || true
else
    docker compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
fi

if [ "$REMOVE_IMAGES" = true ]; then
    echo -e "${YELLOW}🗑️  Removing images...${NC}"
    docker compose -f "$COMPOSE_FILE" down --rmi all 2>/dev/null || true
fi

# Clean up any orphaned containers by name
for container in le-sesame-postgres le-sesame-backend le-sesame-frontend; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        echo -e "   Removing orphaned container: ${container}"
        docker rm -f "$container" 2>/dev/null || true
    fi
done

echo ""
echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo ""
echo -e "To restart services, run:"
echo -e "  ${BLUE}$SCRIPT_DIR/deploy.sh${NC}"
echo ""
