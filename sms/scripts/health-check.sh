#!/bin/bash
# Health check script for production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:80}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

echo "🏥 Starting health checks..."

# Function to check service
check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $service_name... "
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url"); then
        if [ "$response" -eq "$expected_status" ]; then
            echo -e "${GREEN}✓ OK${NC} (HTTP $response)"
            return 0
        else
            echo -e "${RED}✗ FAIL${NC} (HTTP $response)"
            return 1
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Connection failed)"
        return 1
    fi
}

# Function to check database
check_database() {
    echo -n "Checking PostgreSQL... "
    
    if command -v pg_isready >/dev/null 2>&1; then
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ OK${NC}"
            return 0
        else
            echo -e "${RED}✗ FAIL${NC}"
            return 1
        fi
    else
        # Fallback to netcat if pg_isready is not available
        if nc -z "$DB_HOST" "$DB_PORT" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ OK${NC} (port accessible)"
            return 0
        else
            echo -e "${RED}✗ FAIL${NC} (port not accessible)"
            return 1
        fi
    fi
}

# Function to check Redis
check_redis() {
    echo -n "Checking Redis... "
    
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; then
            echo -e "${GREEN}✓ OK${NC}"
            return 0
        else
            echo -e "${RED}✗ FAIL${NC}"
            return 1
        fi
    else
        # Fallback to netcat
        if nc -z "$REDIS_HOST" "$REDIS_PORT" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ OK${NC} (port accessible)"
            return 0
        else
            echo -e "${RED}✗ FAIL${NC} (port not accessible)"
            return 1
        fi
    fi
}

# Run health checks
failed_checks=0

# Check database
if ! check_database; then
    ((failed_checks++))
fi

# Check Redis
if ! check_redis; then
    ((failed_checks++))
fi

# Check backend API
if ! check_service "Backend API" "$BACKEND_URL/health"; then
    ((failed_checks++))
fi

# Check frontend
if ! check_service "Frontend" "$FRONTEND_URL/health"; then
    ((failed_checks++))
fi

# Check API endpoints
if ! check_service "API Root" "$BACKEND_URL/"; then
    ((failed_checks++))
fi

# Summary
echo ""
if [ $failed_checks -eq 0 ]; then
    echo -e "${GREEN}🎉 All health checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ $failed_checks health check(s) failed!${NC}"
    exit 1
fi