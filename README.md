# Take Your Vitamins

A Flask-based API for managing vitamin information with MongoDB.

## Project Structure

```
TakeYourVitamins
│
├── app/                      # Main application directory
│   ├── __init__.py           # App initialization
│   ├── config.py             # Application configuration
│   ├── swagger.py            # Swagger documentation
│   ├── utils/                # Utility functions
│   ├── models/               # Data models
│   ├── routes/               # API routes
│   ├── middleware/           # Middleware components
│   └── db/                   # Database related functionality
│
├── tests/                    # Test directory
│   ├── unit/                 # Unit tests
│   └── utils.py              # Testing utilities
│
├── scripts/                  # Utility scripts
│
├── run.py                    # Application entry point
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── run_local_server.sh       # Script to run local server
├── test_data.json            # Sample data for testing
├── .env                      # Environment variables
├── Makefile                  # Project automation
└── README.md                 # Project documentation
```

## Setup

### Prerequisites

- Python 3.8+ installed
- MongoDB installed and running
- Make (usually pre-installed on most systems)

### Installation

#### Using Make (Recommended)

The project includes a Makefile for easy setup and management:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd TakeYourVitamins
   ```

2. Configure environment variables in `.env` file:
   ```
   MONGO_URI=mongodb://localhost:27017/
   DB_NAME=vitamins_db
   ```

3. Start MongoDB:
   ```
   # On macOS with Homebrew
   brew tap mongodb/brew
   brew install mongodb-community
   brew services start mongodb-community
   
   # On Ubuntu
   sudo systemctl start mongodb

   # On Windows
   mongosh.exe
   ```

4. Run the application with a single command:
   ```
   make run
   ```
   
   This command will:
   - Create a virtual environment if it doesn't exist
   - Install all dependencies
   - Check if MongoDB is running
   - Import sample data if the database is empty
   - Start the Flask application

#### Manual Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd TakeYourVitamins
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables in `.env` file:
   ```
   MONGO_URI=mongodb://localhost:27017/
   DB_NAME=vitamins_db
   ```

5. Ensure MongoDB is running:
   ```
   # On macOS with Homebrew
   brew services start mongodb-community
   
   # On Ubuntu
   sudo systemctl start mongodb
   ```

6. Start the application:
   ```
   ./run_local_server.sh
   ```

   Alternatively:
   ```
   python run.py
   ```

7. Import sample data (in a separate terminal):
   ```
   python scripts/import_data.py
   ```

### Makefile Commands

The project includes a Makefile with the following commands:

- `make setup` - Create virtual environment and install dependencies
- `make venv` - Create virtual environment only
- `make install` - Install dependencies in virtual environment
- `make run` - Complete setup and run the application (creates environment, installs dependencies, checks MongoDB, imports data if needed, and starts the server)
- `make import` - Import sample data into MongoDB
- `make clean` - Remove virtual environment and cached files
- `make help` - Display available commands

### API Documentation

Swagger UI is available at http://localhost:5001/api/docs to explore and test the API interactively.

## Testing and CI/CD

The project includes automated testing and continuous integration using GitHub Actions.

### Running Tests Locally

You can run tests locally using these commands:

```bash
# Run all tests
make test

# Run linting checks
make lint

# Format code with black
make format

# Run all checks (tests, lint, format)
make check
```

### Continuous Integration

This project uses GitHub Actions for continuous integration. The CI pipeline runs whenever code is pushed to the main branch or when a pull request is opened.

The pipeline performs the following tasks:
1. Runs all unit tests with pytest
2. Checks code quality with flake8
3. Verifies code formatting with black
4. Runs pylint for additional code quality checks
5. Generates code coverage reports

The complete configuration can be found in `.github/workflows/ci.yml`.

## API Endpoints

### Vitamins API

- `GET /api/vitamins/` - Get all vitamins or search by name
  - Query parameters:
    - `name` (optional): Filter vitamins by name or alias

- `GET /api/vitamins/<vitamin_id>` - Get a specific vitamin by ID

- `POST /api/vitamins/` - Add a new vitamin
  - Requires JSON body with vitamin data

- `PUT /api/vitamins/<vitamin_id>` - Update an existing vitamin
  - Requires JSON body with vitamin data

- `DELETE /api/vitamins/<vitamin_id>` - Delete a vitamin

- `POST /api/vitamins/import` - Import multiple vitamins
  - Requires JSON array of vitamin data

## Data Model

The vitamin data model includes:

- name: Name of the vitamin
- aliases: List of alternative names
- category: Type/category of supplement
- description: Detailed description
- intakePractices: Guidelines for taking the supplement
  - dosage: Recommended dosage
  - timing: When to take the supplement
  - specialInstructions: Additional instructions
- supplementInteractions: Information about interactions with other supplements
- foodInteractions: Information about interactions with foods
