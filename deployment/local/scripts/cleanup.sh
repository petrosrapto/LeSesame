#!/bin/bash
# Le Sésame - Local Development Cleanup Script
# Stops and removes all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo "  Le Sésame - Local Cleanup"
echo "============================================"
echo ""

cd "$DEPLOY_DIR"

# Parse arguments
REMOVE_VOLUMES=false
for arg in "$@"; do
    case $arg in
        -v|--volumes)
            REMOVE_VOLUMES=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -v, --volumes    Also remove volumes (database data)"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
    esac
done

echo "🛑 Stopping services..."
if [ "$REMOVE_VOLUMES" = true ]; then
    echo "⚠️  Also removing volumes (database data will be lost)"
    docker-compose down -v
else
    docker-compose down
fi

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "To restart services, run:"
echo "  $SCRIPT_DIR/deploy.sh"
echo ""
