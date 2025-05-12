from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/tyv")
DB_NAME = os.getenv("DB_NAME", "tyv")

def get_database():
    """
    Returns a database connection.
    Creates a new connection for each call (safe for Flask multi-threaded apps).
    Raises an exception if the connection fails.
    """
    try:
        client = MongoClient(MONGO_URI)
        # Test the connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        db = client[DB_NAME]
        return db
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise RuntimeError("Could not connect to MongoDB") from e
    except Exception as e:
        logger.error(f"Unexpected error while connecting to MongoDB: {e}")
        raise RuntimeError("Unexpected error during MongoDB connection") from e

def get_collection(collection_name):
    """
    Returns a collection from the database.
    Args:
        collection_name (str): Name of the collection to retrieve.
    Returns:
        pymongo.collection.Collection: The requested collection.
    Raises:
        ValueError: If collection_name is empty or invalid.
    """
    if not collection_name or not isinstance(collection_name, str):
        raise ValueError("Collection name must be a non-empty string")
    database = get_database()
    return database[collection_name]