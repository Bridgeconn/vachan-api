
ENVPATH := vachan-ENV
ACTIVATE_VENV := . $(ENVPATH)/bin/activate &&

SHELL := /bin/bash

.PHONY: pre-requistite venv-configure venv-activate install-dependencies check-package into-database environmental-variables installing-usfmgrammar installing-docker kratosconfig

pre-requisite: #basic python packages to run the makefile
	@if ! dpkg -s python3-pip &> /dev/null; then \
		echo "python3-pip is not installed. Installing..."; \
		sudo apt install -y python3-pip; \
	else \
		echo "python3-pip is already installed."; \
	fi
  
	@if ! dpkg -s python3-venv &> /dev/null; then \
		echo "python3-venv is not installed. Installing..."; \
		sudo apt install -y python3-venv; \
	else \
		echo "python3-venv is already installed."; \
	fi



venv-configure: ## Configure virtual environment and install dependencies
	@echo ">>> Configure virtual environment..."
	python3 -m venv $(ENVPATH)
	@echo ">>> Virtual environment configured..."

venv-activate: ## Activate virtual-env
	@echo ">>> Virtual environment activation..."
	@echo $$(source $(ENVPATH)/bin/activate && python -c "import sys; print(sys.prefix)")

install-dependencies: ## Install dependencies from requirements
	@echo ">>> Installing dependencies..."
	@$(ACTIVATE_VENV) pip install -r requirements.txt

check-package: ## Check if packages from requirements.txt are installed
	@echo ">>> Checking packages..."
	@$(ACTIVATE_VENV) pip install -r requirements.txt --upgrade --quiet && \
	if [ $$? -eq 0 ]; then \
		echo "All packages are installed."; \
	else \
		echo "Some packages are missing or failed to install."; \
	fi

installing-psql:
	@if psql --version | grep -q "15.3"; then \
		echo "You already have psql 15.3 installed."; \
	else \
		read -p "You currently have a different version of psql installed. Do you want to proceed with installing psql 15.3? (y/N) " response; \
		if [[ $$response =~ ^[Yy]$$ ]]; then \
			echo "Installing psql 15.3..."; \
			sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $$(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'; \
			wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo tee /etc/apt/trusted.gpg.d/pgdg.asc &>/dev/null; \
			sudo apt update; \
			sudo apt remove postgresql postgresql-contrib; \
			sudo apt install postgresql-15 postgresql-contrib-15; \
		else \
			echo "Aborted installation."; \
		fi; \
	fi


into-database: ## Accessing the database folder
	sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='vachan_db'" | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE vachan_db"
 
	cd db && sudo -u postgres psql vachan_db < seed_DB.sql



environmental-variables:
	chmod +x setup.sh
	./setup.sh

installing-usfmgrammar:
	sudo apt install npm
	sudo npm install -g usfm-grammar@2.2.0

installing-docker:
	@if docker --version | grep -q "Docker version 24.0."; then \
		echo "You already have Docker 24.0.1 or above installed."; \
	else \
		read -p "Do you want to install/update to the latest Docker version? (y/N) " response; \
		if [[ $$response =~ ^[Yy]$$ ]]; then \
			if docker --version | grep -q "Docker version"; then \
				echo "Removing existing Docker installation..."; \
				for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $$pkg; done; \
			fi; \
			echo "Installing the latest version of Docker..."; \
			sudo apt-get update; \
			sudo apt-get install -y ca-certificates curl gnupg; \
			sudo install -m 0755 -d /etc/apt/keyrings; \
			curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg; \
			sudo chmod a+r /etc/apt/keyrings/docker.gpg; \
			echo "deb [arch=$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu bionic stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null; \
			sudo apt-get update --allow-releaseinfo-change; \
			sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin; \
			if [[ $$? -eq 0 ]]; then \
				echo "Docker has been installed/updated to the latest version."; \
			else \
				echo "Docker installation/update failed. Refer to the Docker installation documentation for manual installation: https://docs.docker.com/engine/install/debian/"; \
			fi \
		else \
			echo "Docker installation/update canceled."; \
		fi \
	fi



kratosconfig:
	cd docker/Kratos_config && docker compose -f quickstart.yml up 


setup:

	make pre-requisite
	make venv-configure
	make venv-activate
	make install-dependencies
	make check-package
	make installing-psql
	make into-database
	make environmental-variables
	make installing-usfmgrammar
	make installing-docker
	make kratosconfig





