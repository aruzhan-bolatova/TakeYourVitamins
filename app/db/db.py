from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv
import logging
from threading import Lock
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/tyv")
DB_NAME = os.getenv("DB_NAME", "tyv")

# Global connection objects
_client = None
_db = None
# Lock for thread safety
_lock = Lock()
# Connection timestamp for monitoring
_last_connection_time = 0
# Max connection age in seconds (30 min)
MAX_CONNECTION_AGE = 1800

def get_database():
    """
    Returns a database connection using connection pooling.
    Creates a new connection if one doesn't exist or if the existing one is too old.
    Implements thread-safe access and reconnection logic.
    """
    global _client, _db, _last_connection_time
    
    with _lock:
        current_time = time.time()
        
        # Check if we need a new connection
        connection_needed = (
            _client is None or 
            _db is None or 
            (current_time - _last_connection_time) > MAX_CONNECTION_AGE
        )
        
        if connection_needed:
            # Close existing connection if it exists
            if _client is not None:
                try:
                    _client.close()
                    logger.info("Closed existing MongoDB connection")
                except Exception as e:
                    logger.warning(f"Error closing MongoDB connection: {e}")
                finally:
                    _client = None
                    _db = None
            
            # Create new connection with retry logic
            retry_count = 0
            max_retries = 3
            retry_delay = 1  # seconds
            
            while retry_count < max_retries:
                try:
                    logger.info(f"Establishing MongoDB connection (attempt {retry_count + 1})")
                    _client = MongoClient(
                        MONGO_URI,
                        serverSelectionTimeoutMS=5000,  # 5 second timeout
                        connectTimeoutMS=5000,
                        socketTimeoutMS=30000,  # 30 second socket timeout
                        maxPoolSize=50,  # Connection pool size
                        minPoolSize=10,
                        maxIdleTimeMS=45000,  # 45 second max idle time
                        waitQueueTimeoutMS=10000  # 10 second wait queue timeout
                    )
                    
                    # Test the connection
                    _client.admin.command('ping')
                    _db = _client[DB_NAME]
                    _last_connection_time = current_time
                    logger.info("Successfully connected to MongoDB")
                    break
                    
                except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"Failed to connect to MongoDB after {max_retries} attempts: {e}")
                        raise RuntimeError("Could not connect to MongoDB") from e
                    
                    logger.warning(f"MongoDB connection attempt {retry_count} failed: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    
                except Exception as e:
                    logger.error(f"Unexpected error while connecting to MongoDB: {e}")
                    raise RuntimeError("Unexpected error during MongoDB connection") from e
        
        return _db

def get_collection(collection_name):
    """
    Returns a collection from the database with error handling.
    Args:
        collection_name (str): Name of the collection to retrieve.
    Returns:
        pymongo.collection.Collection: The requested collection.
    Raises:
        ValueError: If collection_name is empty or invalid.
    """
    if not collection_name or not isinstance(collection_name, str):
        raise ValueError("Collection name must be a non-empty string")
    
    try:
        database = get_database()
        return database[collection_name]
    except Exception as e:
        logger.error(f"Error accessing collection {collection_name}: {e}")
        raise

def close_connection():
    """
    Closes the database connection. This should only be called when the application is shutting down.
    """
    global _client, _db
    
    with _lock:
        if _client:
            try:
                _client.close()
                logger.info("MongoDB connection closed")
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {e}")
            finally:
                _client = None
                _db = None

# Register app shutdown handler to close MongoDB connections
def register_shutdown_handler(app):
    """
    Register a function to close MongoDB connections when the Flask app shuts down.
    """
    @app.teardown_appcontext
    def shutdown_db_connection(exception=None):
        close_connection()