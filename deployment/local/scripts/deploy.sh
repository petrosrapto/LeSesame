#!/bin/bash
# Le Sésame - Local Development Deployment Script
# Builds and starts all services from source

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$DEPLOY_DIR")")"

echo "============================================"
echo "  Le Sésame - Local Development Deployment"
echo "============================================"
echo ""
echo "Deploy Directory: $DEPLOY_DIR"
echo "Project Root: $PROJECT_ROOT"
echo ""

# Check for .env files
if [ ! -f "$DEPLOY_DIR/backend/.env" ]; then
    echo "⚠️  Backend .env not found, copying from .env.example..."
    cp "$DEPLOY_DIR/backend/.env.example" "$DEPLOY_DIR/backend/.env"
fi

if [ ! -f "$DEPLOY_DIR/frontend/.env" ]; then
    echo "⚠️  Frontend .env not found, copying from .env.example..."
    cp "$DEPLOY_DIR/frontend/.env.example" "$DEPLOY_DIR/frontend/.env"
fi

echo "📦 Step 1: Building and starting services..."
cd "$DEPLOY_DIR"
docker-compose up -d --build

echo ""
echo "⏳ Step 2: Waiting for backend to be healthy..."
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend health check timeout (may still be starting)"
    fi
    sleep 2
done

echo ""
echo "⏳ Step 3: Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Frontend health check timeout (may still be starting)"
    fi
    sleep 2
done

echo ""
echo "============================================"
echo "  Deployment Complete!"
echo "============================================"
echo ""
echo "🌐 Frontend:   http://localhost:3000"
echo "🔧 Backend:    http://localhost:8000"
echo "📚 API Docs:   http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose -f $DEPLOY_DIR/docker-compose.yml logs -f"
echo ""
echo "To stop services:"
echo "  $SCRIPT_DIR/cleanup.sh"
echo ""
