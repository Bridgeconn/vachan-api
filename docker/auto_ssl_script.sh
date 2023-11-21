#!/bin/bash

# ------------------------------------------------------------------------------
# Developer Details
# ------------------------------------------------------------------------------
# Name: Uday Kumar
# Contact: [uday.kumar@bridgeconn.com](uday.kumar@bridgeconn.com)
# Date: 21 Nov 2023
# Description: This script sets up and manages a Dockerized Nginx environment 
# with Let's Encrypt SSL, including automatic certificate renewal.
# ------------------------------------------------------------------------------

# Environment variables
NGINX_CONTAINER_NAME="${NGINX_CONTAINER_NAME}"
DOMAIN_NAME="${VACHAN_DOMAIN}"
EMAIL="${EMAIL}"

# Can change as per host letsencrypt path
CERT_PATH="/etc/letsencrypt/."
DOCKER_VOLUME_PATH="./certbot/conf/"

# Stop Nginx container
stop_nginx_container() {
    echo "Stopping Nginx container: $1..."
    docker stop "$1" || { echo "Failed to stop Nginx container"; exit 1; }
}

# Check and free up port 80
free_up_port_80() {
    echo "Checking port 80..."
    PORT_80_PID=$(lsof -t -i:80)
    if [ ! -z "$PORT_80_PID" ]; then
        echo "Port 80 is in use by PID $PORT_80_PID. Killing the process..."
        kill -9 "$PORT_80_PID" || { echo "Failed to kill process on port 80"; exit 1; }
    fi
}

# Install Nginx
install_nginx() {
    if ! command -v nginx &> /dev/null; then
        echo "Nginx not found, installing..."
        apt-get update && apt-get install -y nginx || { echo "Failed to install Nginx"; exit 1; }
    fi
}

# Install Certbot
install_certbot() {
    if ! command -v certbot &> /dev/null; then
        echo "Certbot not found, installing..."
        apt-get update && snap install certbot --classic || { echo "Failed to install Certbot"; exit 1; }
    fi
}

# Create SSL certificate
create_ssl_certificate() {
    local domain="$1"
    local email="$2"
    echo "Creating SSL certificate for $domain..."
    certbot certonly --standalone -d "$domain" --non-interactive --agree-tos --email "$email" || { echo "Failed to create SSL certificate"; exit 1; }
}

# Copy SSL certificate from host to Docker volume
copy_ssl_certificate() {
    local cert_path="$1"
    local docker_volume_path="$2"
    echo "Copying SSL certificate to Docker volume..."
    cp -r "$cert_path" "$docker_volume_path" || { echo "Failed to copy SSL certificate"; exit 1; }
}

# Start Nginx container
start_nginx_container() {
    echo "Starting Nginx container: $1..."
    docker start "$1" || { echo "Failed to start Nginx container"; exit 1; }
}

# Setup automatic renewal of SSL certificate
setup_automatic_ssl_renewal() {
    echo "Setting up automatic SSL certificate renewal..."
    (crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --renew-hook 'docker restart $NGINX_CONTAINER_NAME'") | crontab - || { echo "Failed to setup automatic SSL certificate renewal"; exit 1; }
}

# Main execution
stop_nginx_container "$NGINX_CONTAINER_NAME"
free_up_port_80
install_nginx
install_certbot
create_ssl_certificate "$DOMAIN_NAME" "$EMAIL"
copy_ssl_certificate "$CERT_PATH" "$DOCKER_VOLUME_PATH"
setup_automatic_ssl_renewal
start_nginx_container "$NGINX_CONTAINER_NAME"

echo "Script completed successfully."
