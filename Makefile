.PHONY: setup venv install run clean import help test lint format check windows

# Check for Windows vs Unix
ifeq ($(OS),Windows_NT)
    # Windows settings
    PYTHON = python
    VENV = venv
    PIP = $(VENV)\Scripts\pip
    PYTHON_VENV = $(VENV)\Scripts\python
    RM = rmdir /s /q
    ACTIVATE = $(VENV)\Scripts\activate
    SEP = \\
else
    # Unix settings
    PYTHON = python3
    VENV = venv
    PIP = $(VENV)/bin/pip
    PYTHON_VENV = $(VENV)/bin/python
    RM = rm -rf
    ACTIVATE = . $(VENV)/bin/activate
    SEP = /
endif

help:
	@echo "Available commands:"
	@echo "  make setup      - Create virtual environment and install dependencies"
	@echo "  make venv       - Create virtual environment only"
	@echo "  make install    - Install dependencies in virtual environment"
	@echo "  make run        - Setup environment, install dependencies, and run the Flask application"
	@echo "  make windows    - Run on Windows systems"
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

# Special Windows run target
windows: setup
	@echo "Running Flask application on Windows..."
	@echo "Importing sample data (if needed)..."
	@$(PYTHON_VENV) scripts$(SEP)import_data.py
	@echo "Starting Flask application..."
	@set FLASK_APP=run.py && set FLASK_ENV=development && $(PYTHON_VENV) -m flask run


run: setup
ifeq ($(OS),Windows_NT)
	@$(MAKE) windows
else
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
endif

import:
	@echo "Importing sample data..."
	@$(PYTHON_VENV) scripts$(SEP)import_data.py

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
ifeq ($(OS),Windows_NT)
	@if exist $(VENV) $(RM) $(VENV)
	@if exist __pycache__ $(RM) __pycache__
	@if exist .pytest_cache $(RM) .pytest_cache
	@if exist .coverage del .coverage
	@if exist htmlcov $(RM) htmlcov
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" $(RM) "%%d"
	@for /d /r . %%d in (*.egg-info) do @if exist "%%d" $(RM) "%%d"
	@del /s /q *.pyc > NUL 2>&1
else
	@$(RM) $(VENV) __pycache__ .pytest_cache .coverage htmlcov
	@find . -type d -name __pycache__ -exec $(RM) {} +
	@find . -type d -name "*.egg-info" -exec $(RM) {} +
	@find . -type f -name "*.pyc" -delete
endif
	@echo "Cleanup complete!"

# Default target
.DEFAULT_GOAL := help 