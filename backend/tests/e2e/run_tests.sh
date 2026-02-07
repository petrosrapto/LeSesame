#!/bin/bash
# Le Sésame Backend - E2E Test Runner
#
# This script runs E2E tests against already running Docker containers.
# Make sure the containers are up before running this script.
#
# Prerequisites:
#   - Docker containers running (via deployment/dev/docker-compose.yml)
#   - Backend API accessible at http://localhost:8000
#
# Usage:
#   ./run_tests.sh                           # Run all E2E tests
#   ./run_tests.sh test_auth.py              # Run specific test file
#   ./run_tests.sh test_auth.py::TestLogin   # Run specific test class
#   E2E_API_URL=http://host:port ./run_tests.sh  # Custom API URL

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default API URL (can be overridden via environment variable)
API_URL="${E2E_API_URL:-http://localhost:8000}"

echo -e "${YELLOW}🧪 Le Sésame E2E Test Runner${NC}"
echo "=================================="
echo -e "API URL: ${BLUE}${API_URL}${NC}"
echo -e "Backend Dir: ${BLUE}${BACKEND_DIR}${NC}"
echo ""

# Check if API is available
echo -e "${YELLOW}🔍 Checking API availability...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "${API_URL}/health" > /dev/null 2>&1; then
        HEALTH_RESPONSE=$(curl -s "${API_URL}/health")
        echo -e "${GREEN}✅ API is available!${NC}"
        echo -e "   Health: ${HEALTH_RESPONSE}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo -e "${RED}❌ API not available at ${API_URL}${NC}"
        echo ""
        echo "Make sure the Docker containers are running. Use the deploy script:"
        echo -e "  ${BLUE}cd deployment/dev && ./scripts/deploy.sh${NC}"
        echo ""
        echo "Or build and run locally:"
        echo -e "  ${BLUE}cd deployment/dev && ./scripts/deploy.sh --build${NC}"
        exit 1
    fi
    
    echo -n "."
    sleep 1
done

# Change to backend directory
cd "$BACKEND_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "\n${YELLOW}🐍 Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Determine test path
if [ -n "$1" ]; then
    # If argument contains ::, it's a specific test, use as-is
    if [[ "$1" == *"::"* ]]; then
        TEST_PATH="tests/e2e/$1"
    # If argument ends with .py, it's a test file
    elif [[ "$1" == *.py ]]; then
        TEST_PATH="tests/e2e/$1"
    else
        TEST_PATH="tests/e2e/$1"
    fi
else
    TEST_PATH="tests/e2e"
fi

# Run the E2E tests
echo -e "\n${YELLOW}🧪 Running E2E tests...${NC}"
echo "=================================="
echo -e "Test path: ${BLUE}${TEST_PATH}${NC}"
echo ""

export E2E_API_URL="${API_URL}"
pytest "${TEST_PATH}" -v --tb=short -x

TEST_EXIT_CODE=$?

echo ""
echo "=================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All E2E tests passed!${NC}"
else
    echo -e "${RED}❌ Some E2E tests failed${NC}"
fi

exit $TEST_EXIT_CODE
