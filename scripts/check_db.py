#!/usr/bin/env python3
"""
Simple script to check if the database has vitamins data.
Returns exit code 0 if data exists, 1 if empty.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

def check_database():
    """Check if vitamins collection has data."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get MongoDB connection info
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('DB_NAME', 'vitamins_db')
        
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Check if vitamins collection has records
        count = db['vitamins'].count_documents({})
        
        # Close connection
        client.close()
        
        # Return True if data exists, False if empty
        return count > 0
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        return False

if __name__ == "__main__":
    has_data = check_database()
    exit(0 if has_data else 1) 