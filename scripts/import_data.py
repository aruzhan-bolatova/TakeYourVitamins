#!/usr/bin/env python3
"""
Script to import vitamin data into MongoDB.
"""
import os
import sys
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory to path to enable imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def import_vitamins_from_json(json_file_path):
    """
    Import vitamin data from a JSON file into MongoDB.
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Get MongoDB connection info
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('DB_NAME', 'vitamins_db')
        
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db['vitamins']
        
        # Read the JSON file
        with open(json_file_path, 'r') as file:
            vitamins_data = json.load(file)
        
        # Import the data
        ids = []
        for vitamin in vitamins_data:
            # Remove the id field if present
            if 'id' in vitamin:
                del vitamin['id']
            
            result = collection.insert_one(vitamin)
            ids.append(str(result.inserted_id))
        
        print(f"Successfully imported {len(ids)} vitamins.")
        print("Imported IDs:", ids)
        
        # Close connection
        client.close()
        
        return True
    except Exception as e:
        print(f"Error importing data: {str(e)}")
        return False

if __name__ == "__main__":
    # If a file path is provided as an argument, use it
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default to test_data.json in the project root
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_data.json'))
    
    print(f"Importing data from: {file_path}")
    import_vitamins_from_json(file_path) 