from app.db.db import get_collection
from app.db.constants import VITAMINS_COLLECTION
from bson import ObjectId
import json

def insert_vitamin(vitamin_data):
    """
    Insert a new vitamin record.
    """
    # Remove the id field if present (MongoDB will generate one)
    if 'id' in vitamin_data:
        del vitamin_data['id']
    
    collection = get_collection(VITAMINS_COLLECTION)
    result = collection.insert_one(vitamin_data)
    return str(result.inserted_id)

def get_vitamin_by_id(vitamin_id):
    """
    Get a vitamin by its ID.
    """
    collection = get_collection(VITAMINS_COLLECTION)
    result = collection.find_one({"_id": ObjectId(vitamin_id)})
    if result:
        result["id"] = str(result["_id"])
        del result["_id"]
    return result

def get_all_vitamins():
    """
    Get all vitamins.
    """
    collection = get_collection(VITAMINS_COLLECTION)
    vitamins = list(collection.find())
    for vitamin in vitamins:
        vitamin["id"] = str(vitamin["_id"])
        del vitamin["_id"]
    return vitamins

def search_vitamins_by_name(name):
    """
    Search vitamins by name or aliases.
    """
    collection = get_collection(VITAMINS_COLLECTION)
    vitamins = list(collection.find({
        "$or": [
            {"name": {"$regex": name, "$options": "i"}},
            {"aliases": {"$elemMatch": {"$regex": name, "$options": "i"}}}
        ]
    }))
    
    for vitamin in vitamins:
        vitamin["id"] = str(vitamin["_id"])
        del vitamin["_id"]
    return vitamins

def update_vitamin(vitamin_id, vitamin_data):
    """
    Update a vitamin record.
    """
    # Remove the id field if present
    if 'id' in vitamin_data:
        del vitamin_data['id']
        
    collection = get_collection(VITAMINS_COLLECTION)
    result = collection.update_one(
        {"_id": ObjectId(vitamin_id)},
        {"$set": vitamin_data}
    )
    return result.modified_count > 0

def delete_vitamin(vitamin_id):
    """
    Delete a vitamin record.
    """
    collection = get_collection(VITAMINS_COLLECTION)
    result = collection.delete_one({"_id": ObjectId(vitamin_id)})
    return result.deleted_count > 0

def import_vitamins_from_json(json_data):
    """
    Import multiple vitamins from JSON data.
    """
    vitamins = json.loads(json_data) if isinstance(json_data, str) else json_data
    ids = []
    
    for vitamin in vitamins:
        # Remove the id field if present
        if 'id' in vitamin:
            del vitamin['id']
        
        collection = get_collection(VITAMINS_COLLECTION)
        result = collection.insert_one(vitamin)
        ids.append(str(result.inserted_id))
    
    return ids
