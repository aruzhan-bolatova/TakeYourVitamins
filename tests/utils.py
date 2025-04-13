"""Test utilities for the TakeYourVitamins application."""
import os
import sys
import tempfile
from unittest.mock import MagicMock

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


def create_mock_mongo_client(collection_data=None):
    """Create a mock MongoDB client for testing.
    
    Args:
        collection_data: A dictionary mapping collection names to lists of documents
                        to be returned by find() calls.
    
    Returns:
        A mock MongoClient object that can be used in tests.
    """
    if collection_data is None:
        collection_data = {}
    
    mock_client = MagicMock()
    mock_db = MagicMock()
    
    # Set up collections based on provided data
    mock_collections = {}
    for coll_name, docs in collection_data.items():
        mock_collection = MagicMock()
        mock_collection.find.return_value = docs
        mock_collection.count_documents.return_value = len(docs)
        mock_collections[coll_name] = mock_collection
    
    # Setup the __getitem__ methods
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__ = lambda key: mock_collections.get(key, MagicMock())
    
    return mock_client


def create_test_env_file():
    """Create a temporary .env file for testing.
    
    Returns:
        tuple: (env_file_path, original_env_vars)
        - env_file_path: Path to the temporary .env file
        - original_env_vars: Dictionary of original environment variables that were set
    """
    # Save original environment variables
    original_env_vars = {}
    env_vars_to_save = [
        'MONGO_URI', 'DB_NAME', 'SECRET_KEY', 'JWT_SECRET_KEY'
    ]
    
    for var in env_vars_to_save:
        if var in os.environ:
            original_env_vars[var] = os.environ[var]
    
    # Create temporary .env file
    fd, env_path = tempfile.mkstemp(prefix='.env_test_')
    with os.fdopen(fd, 'w') as f:
        f.write("# Test environment variables\n")
        f.write("MONGO_URI=mongodb://testuser:testpass@localhost:27017/\n")
        f.write("DB_NAME=test_vitamins_db\n")
        f.write("SECRET_KEY=test_secret_key\n")
        f.write("JWT_SECRET_KEY=test_jwt_secret_key\n")
    
    return env_path, original_env_vars


def cleanup_test_env(env_file_path, original_env_vars):
    """Clean up the temporary .env file and restore original environment variables.
    
    Args:
        env_file_path: Path to the temporary .env file to remove
        original_env_vars: Dictionary of original environment variables to restore
    """
    # Remove temporary .env file
    if os.path.exists(env_file_path):
        os.remove(env_file_path)
    
    # Clear any test environment variables
    env_vars_to_clear = [
        'MONGO_URI', 'DB_NAME', 'SECRET_KEY', 'JWT_SECRET_KEY'
    ]
    
    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]
    
    # Restore original environment variables
    for var, value in original_env_vars.items():
        os.environ[var] = value
