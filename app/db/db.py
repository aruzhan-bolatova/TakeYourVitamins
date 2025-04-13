from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")

client = None
db = None

def get_database():
    """
    Returns a database connection.
    Creates a new connection if one doesn't exist.
    """
    global client, db
    if not client:
        client = MongoClient(mongo_uri)
        db = client[db_name]
    return db

def get_collection(collection_name):
    """
    Returns a collection from the database.
    """
    database = get_database()
    return database[collection_name]

def close_connection():
    """
    Closes the database connection.
    """
    global client
    if client:
        client.close()
        client = None
