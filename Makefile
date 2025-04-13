.PHONY: setup venv install run clean import help

# Python interpreter to use
PYTHON = python3
VENV = venv
PIP = $(VENV)/bin/pip
PYTHON_VENV = $(VENV)/bin/python

help:
	@echo "Available commands:"
	@echo "  make setup      - Create virtual environment and install dependencies"
	@echo "  make venv       - Create virtual environment only"
	@echo "  make install    - Install dependencies in virtual environment"
	@echo "  make run        - Setup environment, install dependencies, and run the Flask application"
	@echo "  make import     - Import sample data into MongoDB"
	@echo "  make clean      - Remove virtual environment and cached files"

setup: venv install

venv:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created!"

install: venv
	@echo "Installing dependencies..."
	@$(PIP) install -r requirements.txt
	@echo "Dependencies installed!"

run: setup
	@echo "Checking if MongoDB is running..."
	@if ! pgrep -x mongod > /dev/null; then \
		echo "⚠️  MongoDB is not running. Please start it before running the application."; \
		echo "You may need to run: brew services start mongodb-community"; \
		exit 1; \
	fi
	@echo "MongoDB is running."
	
	@# Check if data needs to be imported using dedicated script
	@echo "Checking if database needs initialization..."
	@$(PYTHON_VENV) scripts/check_db.py || \
	(echo "Database appears empty. Importing sample data..." && \
	$(PYTHON_VENV) scripts/import_data.py && \
	echo "Sample data imported successfully!")
	
	@echo "Starting Flask application..."
	@FLASK_APP=run.py FLASK_ENV=development $(PYTHON_VENV) run.py

import:
	@echo "Importing sample data..."
	@$(PYTHON_VENV) scripts/import_data.py

clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV) __pycache__ .pytest_cache .coverage
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete!"

# Default target
.DEFAULT_GOAL := help 