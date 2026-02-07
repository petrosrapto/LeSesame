#!/bin/bash
# Le Sésame - Dev Environment Cleanup Script
# Stops and removes all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo "  Le Sésame - Dev Cleanup"
echo "============================================"
echo ""

cd "$DEPLOY_DIR"

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
            echo "  -v, --volumes    Also remove volumes (database data)"
            echo "  -i, --images     Also remove pulled images"
            echo "  -a, --all        Remove volumes and images"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
    esac
done

echo "🛑 Stopping services..."
if [ "$REMOVE_VOLUMES" = true ]; then
    echo "⚠️  Also removing volumes"
    docker-compose down -v
else
    docker-compose down
fi

if [ "$REMOVE_IMAGES" = true ]; then
    echo "🗑️  Removing images..."
    docker-compose down --rmi all 2>/dev/null || true
fi

echo ""
echo "✅ Cleanup complete!"
echo ""
