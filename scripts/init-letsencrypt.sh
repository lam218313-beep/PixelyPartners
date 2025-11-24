#!/bin/bash

# Initialize Let's Encrypt SSL Certificates for Pixely Partners
# Domain: partners.pixely.pe
# Email: lsckryl@gmail.com

set -e

# Configuration
DOMAIN="partners.pixely.pe"
EMAIL="lsckryl@gmail.com"
DATA_PATH="./certbot"
NGINX_CONF_PATH="./nginx/conf.d"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Let's Encrypt SSL Initialization${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Domain: ${YELLOW}${DOMAIN}${NC}"
echo -e "Email: ${YELLOW}${EMAIL}${NC}"
echo ""

# Check if certificates already exist
if [ -d "$DATA_PATH/conf/live/$DOMAIN" ]; then
    echo -e "${YELLOW}⚠️  Certificates already exist for $DOMAIN${NC}"
    read -p "Do you want to recreate them? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ Using existing certificates${NC}"
        exit 0
    fi
    echo -e "${YELLOW}🗑️  Removing existing certificates...${NC}"
    sudo rm -rf "$DATA_PATH/conf/live/$DOMAIN"
    sudo rm -rf "$DATA_PATH/conf/archive/$DOMAIN"
    sudo rm -f "$DATA_PATH/conf/renewal/$DOMAIN.conf"
fi

# Check if staging mode
echo ""
read -p "Use Let's Encrypt STAGING server? (recommended for testing) (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    STAGING_ARG=""
    echo -e "${RED}⚠️  PRODUCTION MODE: Rate limits apply!${NC}"
else
    STAGING_ARG="--staging"
    echo -e "${GREEN}✅ STAGING MODE: Testing with fake certificates${NC}"
fi

# Ensure directories exist
echo -e "${YELLOW}📁 Creating directory structure...${NC}"
mkdir -p "$DATA_PATH/www"
mkdir -p "$DATA_PATH/conf/live/$DOMAIN"

# Create dummy certificate for initial nginx start
echo -e "${YELLOW}🔧 Creating dummy certificate for initial setup...${NC}"
docker compose run --rm --entrypoint "\
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout /etc/letsencrypt/live/$DOMAIN/privkey.pem \
    -out /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
    -subj '/CN=localhost'" certbot

# Create dhparam.pem if it doesn't exist
if [ ! -f "$DATA_PATH/conf/dhparam.pem" ]; then
    echo -e "${YELLOW}🔐 Generating dhparam (this may take a while)...${NC}"
    docker compose run --rm --entrypoint "\
        openssl dhparam -out /etc/letsencrypt/dhparam.pem 2048" certbot
fi

# Start nginx with dummy certificate
echo -e "${YELLOW}🚀 Starting nginx with dummy certificate...${NC}"
# Temporarily use default.conf (HTTP only)
docker compose up -d nginx

echo -e "${YELLOW}⏳ Waiting for nginx to start...${NC}"
sleep 5

# Request real certificate
echo -e "${YELLOW}📜 Requesting Let's Encrypt certificate...${NC}"
docker compose run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
    $STAGING_ARG \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d $DOMAIN" certbot

# Check if certificate was obtained successfully
if [ -f "$DATA_PATH/conf/live/$DOMAIN/fullchain.pem" ]; then
    echo -e "${GREEN}✅ Certificate obtained successfully!${NC}"
    
    # Switch to SSL configuration
    echo -e "${YELLOW}🔄 Switching to SSL configuration...${NC}"
    
    # Reload nginx with SSL config
    docker compose exec nginx nginx -s reload
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ SSL SETUP COMPLETE!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "Your site is now available at:"
    echo -e "${GREEN}https://$DOMAIN${NC}"
    echo ""
    echo -e "Certificate details:"
    docker compose run --rm --entrypoint "\
        certbot certificates" certbot
else
    echo -e "${RED}❌ Failed to obtain certificate${NC}"
    echo -e "${YELLOW}Check logs above for errors${NC}"
    exit 1
fi
