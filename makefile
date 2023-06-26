
ENVPATH := vachan-ENV
ACTIVATE_VENV := . $(ENVPATH)/bin/activate &&

SHELL := /bin/bash

.PHONY: venv-configure venv-activate install-dependencies check-package into-database environmental-variables installing-usfmgrammar installing-docker kratosconfig

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

installing-psql: #installing psql
	sudo apt update
	sudo apt install postgresql postgresql-contrib



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
	sudo apt install gnome-terminal

	sudo apt-get update 
	sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin


kratosconfig:
	cd docker/Kratos_config && docker-compose -f quickstart.yml up 


setup:

	make venv-configure
	make venv-activate
	make install-dependencies
	make check-package
	make install-psql
	make into-database
	make environmental-variables
	make installing-usfmgrammar
	make installing-docker
	make kratosconfig



