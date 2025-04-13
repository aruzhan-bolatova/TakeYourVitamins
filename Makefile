.PHONY: setup venv install run clean import help test lint format check

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
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting checks"
	@echo "  make format     - Format code with black"
	@echo "  make check      - Run tests, lint, and format checks"

setup: venv install

venv:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created!"

install: venv
	@echo "Installing dependencies..."
	@$(PIP) install -r requirements.txt
	@$(PIP) install -r requirements-dev.txt
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

test: install
	@echo "Running tests..."
	@$(PYTHON_VENV) -m pytest

lint: install
	@echo "Running linting checks..."
	@$(PYTHON_VENV) -m flake8 app scripts tests
	@$(PYTHON_VENV) -m pylint app scripts tests

format: install
	@echo "Formatting code with black..."
	@$(PYTHON_VENV) -m black app scripts tests

check: install
	@$(MAKE) test
	@$(MAKE) lint
	@$(MAKE) format

clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV) __pycache__ .pytest_cache .coverage htmlcov
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete!"

# Default target
.DEFAULT_GOAL := help 