#!/bin/bash

# ------------------------------------------------------------------------------
# Developer Details
# ------------------------------------------------------------------------------
# Name: Uday Kumar
# Contact: uday.kumar@bridgeconn.com
# Date: 21 Nov 2023
# Description: This script sets up and manages Let's Encrypt SSL, including automatic certificate renewal.
# ------------------------------------------------------------------------------


# Load environment variables
if [ -f prod.env ]; then
    source prod.env
else
    echo "prod.env file not found"
    exit 1
fi

# Configuration variables
NGINX_CONTAINER_NAME="docker-web-server-with-cert-1"
SSL_CERTS_DIR="/certbot/conf"
WEBROOT_DIR="/certbot/www"

# Generate SSL certificates
generate_certificates() {
    echo "Generating SSL certificates for $DOMAIN..."

    docker run --rm -it \
        -v "$(pwd)${SSL_CERTS_DIR}:/etc/letsencrypt" \
        -p 80:80 \
        certbot/certbot certonly --standalone \
        --email "${CERTBOT_EMAIL}" --agree-tos --no-eff-email \
        -d "${VACHAN_DOMAIN}" --non-interactive --verbose

    if [ $? -ne 0 ]; then
        echo "Error: Failed to generate SSL certificates."
        exit 1
    fi
}

# Renew SSL certificates
renew_certificates() {
    echo "Renewing SSL certificates for $DOMAIN..."

    docker run --rm \
        -v "$(pwd)${SSL_CERTS_DIR}:/etc/letsencrypt" \
        certbot/certbot renew --non-interactive --verbose

    if [ $? -ne 0 ]; then
        echo "Error: Failed to renew SSL certificates."
        exit 1
    fi
}

# Restart Nginx container
start_nginx_container() {
    echo "Starting Nginx container: ${NGINX_CONTAINER_NAME}..."
    docker restart "${NGINX_CONTAINER_NAME}" || { echo "Failed to start Nginx container"; exit 1; }
}


# Execute the functions
if [ ! -e "${SSL_CERTS_DIR}/live/${DOMAIN}/fullchain.pem" ]; then
    generate_certificates
    start_nginx_container
else
    renew_certificates
fi


echo "Script completed successfully."