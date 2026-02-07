#!/bin/bash
# Le Sésame Backend - Docker Entrypoint Script
# This script runs database migrations before starting the application

set -e

echo "============================================"
echo "  Le Sésame Backend - Starting"
echo "============================================"

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    # Try to connect to PostgreSQL using Python
    if python -c "
import sys
import asyncio
import asyncpg

async def check_db():
    try:
        # Parse DATABASE_URL
        import os
        url = os.environ.get('DATABASE_URL', '')
        # Extract connection params from URL
        # postgresql+asyncpg://user:pass@host:port/db
        if 'asyncpg://' in url:
            url = url.replace('postgresql+asyncpg://', '')
            auth, rest = url.split('@')
            user, password = auth.split(':')
            host_port, db = rest.split('/')
            host, port = host_port.split(':') if ':' in host_port else (host_port, '5432')
            
            conn = await asyncpg.connect(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=db
            )
            await conn.close()
            return True
    except Exception as e:
        print(f'DB not ready: {e}', file=sys.stderr)
        return False
    return False

sys.exit(0 if asyncio.run(check_db()) else 1)
" 2>/dev/null; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Attempt $RETRY_COUNT/$MAX_RETRIES - PostgreSQL not ready yet..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Failed to connect to PostgreSQL after $MAX_RETRIES attempts"
    exit 1
fi

# Run database migrations
echo ""
echo "🔄 Running database migrations..."
cd /app

# Run alembic migrations
if python -m alembic upgrade head; then
    echo "✅ Database migrations completed successfully!"
else
    echo "❌ Database migrations failed!"
    exit 1
fi

echo ""
echo "🚀 Starting application server..."
echo "============================================"

# Execute the main command (uvicorn)
exec "$@"
