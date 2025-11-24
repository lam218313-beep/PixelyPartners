#!/bin/bash

# Quick Health Check Script for Pixely Partners Infrastructure
# Checks all services and SSL configuration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Pixely Partners - Health Check${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. Check Docker Services
echo -e "${YELLOW}📦 Checking Docker Services...${NC}"
if docker compose ps | grep -q "Up"; then
    RUNNING=$(docker compose ps --filter "status=running" | grep -c "Up" || echo "0")
    echo -e "${GREEN}✅ Docker services running: $RUNNING${NC}"
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
else
    echo -e "${RED}❌ No Docker services running${NC}"
fi
echo ""

# 2. Check Nginx
echo -e "${YELLOW}🌐 Checking Nginx...${NC}"
if docker compose ps nginx | grep -q "Up"; then
    echo -e "${GREEN}✅ Nginx is running${NC}"
    
    # Test configuration
    if docker compose exec nginx nginx -t 2>&1 | grep -q "successful"; then
        echo -e "${GREEN}✅ Nginx configuration is valid${NC}"
    else
        echo -e "${RED}❌ Nginx configuration has errors${NC}"
    fi
else
    echo -e "${RED}❌ Nginx is not running${NC}"
fi
echo ""

# 3. Check SSL Certificates
echo -e "${YELLOW}🔐 Checking SSL Certificates...${NC}"
if [ -f "./certbot/conf/live/partners.pixely.pe/fullchain.pem" ]; then
    echo -e "${GREEN}✅ SSL certificate found${NC}"
    
    # Check expiry
    EXPIRY=$(docker compose run --rm certbot certificates 2>/dev/null | grep "Expiry Date" | head -1)
    if [ ! -z "$EXPIRY" ]; then
        echo -e "${GREEN}$EXPIRY${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  SSL certificate not found (run init-letsencrypt.sh)${NC}"
fi
echo ""

# 4. Check Frontend
echo -e "${YELLOW}📊 Checking Frontend (Streamlit)...${NC}"
if docker compose ps frontend | grep -q "Up"; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
    
    # Check if accessible internally
    if docker compose exec frontend curl -f -s http://localhost:8501 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend responding on port 8501${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend not responding (may be still starting)${NC}"
    fi
else
    echo -e "${RED}❌ Frontend is not running${NC}"
fi
echo ""

# 5. Check API
echo -e "${YELLOW}🚀 Checking API (FastAPI)...${NC}"
if docker compose ps api | grep -q "Up"; then
    echo -e "${GREEN}✅ API is running${NC}"
    
    # Check if accessible internally
    if docker compose exec api curl -f -s http://localhost:8000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API responding on port 8000${NC}"
    else
        echo -e "${YELLOW}⚠️  API not responding (may be still starting)${NC}"
    fi
else
    echo -e "${RED}❌ API is not running${NC}"
fi
echo ""

# 6. Check Database
echo -e "${YELLOW}🗄️  Checking Database (PostgreSQL)...${NC}"
if docker compose ps db | grep -q "Up"; then
    echo -e "${GREEN}✅ Database is running${NC}"
    
    # Check if healthy
    if docker compose exec db pg_isready -U pixely_user -d pixely_db > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Database accepting connections${NC}"
    else
        echo -e "${YELLOW}⚠️  Database not ready${NC}"
    fi
else
    echo -e "${RED}❌ Database is not running${NC}"
fi
echo ""

# 7. Check Orchestrator
echo -e "${YELLOW}⚙️  Checking Orchestrator...${NC}"
if docker compose ps orchestrator | grep -q "Up"; then
    echo -e "${GREEN}✅ Orchestrator is running${NC}"
    
    # Check cron
    if docker compose exec orchestrator ps aux 2>/dev/null | grep -q "cron"; then
        echo -e "${GREEN}✅ Cron service is active${NC}"
    else
        echo -e "${YELLOW}⚠️  Cron service not detected${NC}"
    fi
else
    echo -e "${RED}❌ Orchestrator is not running${NC}"
fi
echo ""

# 8. Check Public Access (if online)
echo -e "${YELLOW}🌍 Checking Public Access...${NC}"
if command -v curl &> /dev/null; then
    # Check HTTP redirect
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://partners.pixely.pe 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" == "301" ] || [ "$HTTP_CODE" == "302" ]; then
        echo -e "${GREEN}✅ HTTP redirects to HTTPS (${HTTP_CODE})${NC}"
    elif [ "$HTTP_CODE" == "000" ]; then
        echo -e "${YELLOW}⚠️  Cannot reach partners.pixely.pe (check DNS/firewall)${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTP response: ${HTTP_CODE}${NC}"
    fi
    
    # Check HTTPS
    HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://partners.pixely.pe 2>/dev/null || echo "000")
    if [ "$HTTPS_CODE" == "200" ]; then
        echo -e "${GREEN}✅ HTTPS is working (${HTTPS_CODE})${NC}"
    elif [ "$HTTPS_CODE" == "000" ]; then
        echo -e "${YELLOW}⚠️  Cannot reach HTTPS (SSL not configured yet?)${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTPS response: ${HTTPS_CODE}${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  curl not installed, skipping public access check${NC}"
fi
echo ""

# 9. Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📋 Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Domain: ${GREEN}partners.pixely.pe${NC}"
echo -e "Email: ${GREEN}lsckryl@gmail.com${NC}"
echo -e "Public URL: ${GREEN}https://partners.pixely.pe${NC}"
echo ""
echo -e "Internal Services:"
echo -e "  - API: ${YELLOW}http://api:8000${NC} (internal only)"
echo -e "  - Adminer: ${YELLOW}http://adminer:8080${NC} (internal only)"
echo -e "  - Database: ${YELLOW}postgresql://db:5432${NC} (internal only)"
echo ""
echo -e "${YELLOW}💡 Tip: Run 'docker compose logs -f' to see real-time logs${NC}"
echo ""
