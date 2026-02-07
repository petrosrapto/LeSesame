#!/bin/bash
# Le Sésame - Dev Environment Deployment Script
# For deploying pre-built images to dev/staging servers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo "  Le Sésame - Dev Environment Deployment"
echo "============================================"
echo ""
echo "Deploy Directory: $DEPLOY_DIR"
echo ""

# Verify .env files exist
if [ ! -f "$DEPLOY_DIR/backend/.env" ]; then
    echo "❌ Backend .env not found!"
    echo "   Create it from .env.example with required values"
    exit 1
fi

if [ ! -f "$DEPLOY_DIR/frontend/.env" ]; then
    echo "❌ Frontend .env not found!"
    echo "   Create it from .env.example with required values"
    exit 1
fi

# Check for required environment variables
source "$DEPLOY_DIR/backend/.env"
if [ -z "$BACKEND_IMAGE" ]; then
    echo "❌ BACKEND_IMAGE not set in backend/.env"
    exit 1
fi

source "$DEPLOY_DIR/frontend/.env"
if [ -z "$FRONTEND_IMAGE" ]; then
    echo "❌ FRONTEND_IMAGE not set in frontend/.env"
    exit 1
fi

echo "📦 Step 1: Stopping existing containers..."
cd "$DEPLOY_DIR"
docker-compose down 2>/dev/null || true

echo ""
echo "🔄 Step 2: Pulling latest images..."
docker-compose pull

echo ""
echo "🚀 Step 3: Starting services..."
docker-compose up -d

echo ""
echo "⏳ Step 4: Waiting for backend to be healthy..."
for i in {1..60}; do
    if docker exec le-sesame-backend curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "⚠️  Backend health check timeout"
    fi
    sleep 2
done

echo ""
echo "⏳ Step 5: Waiting for frontend to be ready..."
for i in {1..60}; do
    if docker exec le-sesame-frontend wget --no-verbose --tries=1 --spider http://localhost:3000/ 2>/dev/null; then
        echo "✅ Frontend is ready"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "⚠️  Frontend health check timeout"
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
echo "View logs with:"
echo "  docker-compose logs -f"
echo ""
