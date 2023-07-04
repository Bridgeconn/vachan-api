#!/bin/bash

echo 'export VACHAN_POSTGRES_HOST="localhost"' >> ~/.bashrc
echo 'export VACHAN_POSTGRES_PORT="5432"' >> ~/.bashrc
echo 'export VACHAN_POSTGRES_USER="postgres"' >> ~/.bashrc

read -r -p "Enter a password for the postgres: " password
echo 'export VACHAN_POSTGRES_PASSWORD="'$password'"' >> ~/.bashrc

echo 'export VACHAN_POSTGRES_PASSWORD="password"' >> ~/.bashrc
echo 'export VACHAN_POSTGRES_DATABASE="vachan1_db"' >> ~/.bashrc
echo 'export VACHAN_POSTGRES_DATA_DIR="/vachan-api"' >> ~/.bashrc
echo 'export VACHAN_LOGGING_LEVEL="WARNING"' >> ~/.bashrc
echo 'export VACHAN_KRATOS_ADMIN_URL="http://127.0.0.1:4434/"' >> ~/.bashrc
echo 'export VACHAN_KRATOS_PUBLIC_URL="http://127.0.0.1:4433/"' >> ~/.bashrc

read -p "Please provide a valid email address for the SuperAdmin username. Your SuperAdmin email ID is:" super_email
echo 'export VACHAN_SUPER_USERNAME="'$super_email'"' >> ~/.bashrc

read -r -p "Enter a strong password for the super admin: at least 8 characters, mixed case, numbers, and symbols." super_password
echo 'export VACHAN_SUPER_PASSWORD="'$super_password'"' >> ~/.bashrc

read -p "Press Enter to make necessary changes in .bashrc file and Click save"

echo ""   # Add a newline here

source ~/.bashrc
gedit ~/.bashrc
# tail -n 15 ~/.bashrc
