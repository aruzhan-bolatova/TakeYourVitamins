''' 
Explanation of Endpoints
GET /api/supplements/:
    Retrieves a list of supplements.
    Uses the Supplement.search method to query the database.
    
    test: GET
    - http://10.228.244.25:5001/api/supplements/?search=aloe&field=aliases
    - http://10.228.244.25:5001/api/supplements/
    
GET /api/supplements/<supplement_id>:
    Retrieves a specific supplement by its supplementId.
    Uses the Supplement.find_by_id method to fetch the supplement.
    
    test: GET 
    - http://10.228.244.25:5001/api/supplements/67fe1342c0edae0f50b5737a
    

POST /api/supplements/:
    Creates a new supplement.
    Validates the incoming data using Supplement.validate_data.
    Inserts the supplement into the database.
    
    test: POST http://10.228.244.25:5001/api/supplements/
        Content-Type: application/json
        {
            "supplementId": "SUPP101",
            "name": "Vitamin C",
            "aliases": ["Ascorbic Acid"],
            "description": "Boosts immunity and acts as an antioxidant.",
            "intakePractices": {
                "dosage": "500mg daily",
                "timing": "Morning",
                "specialInstructions": "Take with food."
            },
            "scientificDetails": {
                "benefits": ["Boosts immunity", "Antioxidant"],
                "sideEffects": ["Rare at recommended doses"]
            },
            "category": "Vitamins",
            "updatedAt": null
        }
        
PUT /api/supplements/<supplement_id>:
    Updates an existing supplement by its supplementId.
    Validates the incoming data and updates the document in the database using Supplement.update.
    
    test: PUT http://10.228.244.25:5001/api/supplements/67fe1342c0edae0f50b5737a
        {
        "description": "Updated description for Vitamin C."
        }

DELETE /api/supplements/<supplement_id>:
    Deletes a supplement by its supplementId.
    Supports soft delete by default (?soft=true), but can perform a hard delete if ?soft=false is passed.
    Uses the Supplement.delete method to perform the deletion.

GET /api/supplements/autocomplete:
    Provides autocomplete suggestions for supplement names or aliases.
    Uses regex to search in both 'name' and 'aliases' fields.
    
    test: GET http://10.228.244.25:5001/api/supplements/autocomplete?search=vit
    sample result: [
    {
        "id": "661452c063c2a1df64d81412",
        "name": "Vitamin C"
    },
    {
        "id": "661452c063c2a1df64d81413",
        "name": "Multivitamin"
    }
]
    
'''

from flask import Blueprint, jsonify, request
from app.models.supplement import Supplement
from app.models.user import User
# Import the database connection function
from app.db.db import get_database as get_db
from bson.objectid import ObjectId  # Import ObjectId to handle MongoDB _id
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity, 
                               get_jwt, current_user)
from app.middleware.auth import check_user_access, admin_required
from app.models.interaction import Interaction

# Create the blueprint
bp = Blueprint('supplements', __name__, url_prefix='/api/supplements')

def admin_required(user_id):
    """Check if user has admin role"""
    user = User.find_by_id(user_id)
    if not user or user.role != 'admin':
        return False
    return True

@bp.route('/', methods=['GET'])
def get_supplements():
    """Get a list of supplements"""
    search_query = request.args.get('search', '')  # Optional search query
    supplements = Supplement.search(search_query, field='name')  # Search by name
    return jsonify([supplement.to_dict() for supplement in supplements]), 200


@bp.route('/<string:supplement_id>', methods=['GET'])
def get_supplement_by_id(supplement_id):
    """Get a specific supplement by its ID"""
    try:
        # Convert the string ID to ObjectId
        _id = ObjectId(supplement_id)
        supplement = Supplement.find_by_id(_id)
        if not supplement:
            return jsonify({"error": "Supplement not found"}), 404
        return jsonify(supplement.to_dict()), 200
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400


@bp.route('/autocomplete', methods=['GET'])
def autocomplete_supplements():
    """Get autocomplete suggestions for supplements by name or aliases"""
    try:
        search_query = request.args.get('search', '')
        if not search_query:
            return jsonify([]), 200  # Return empty list if no query provided

        results = Supplement.autocomplete(search_query)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500
    
@bp.route('/', methods=['POST'])
@jwt_required()
def create_supplement():
    """Create a new supplement"""
    try:
        supplement_data = request.json
        
        if supplement_data is None:  # Check if the request body is not JSON
            return jsonify({"error": "Missing JSON in request"}), 400
        
        if not supplement_data:  # Check for empty data
            return jsonify({"error": "Empty supplement data"}), 400

        supplement = Supplement(supplement_data)
        supplement.validate_data(supplement_data)  # Validate the incoming data
        
        # Insert the supplement into the database
        db = get_db()
        result = db.Supplements.insert_one(supplement.to_dict())
        
        if not result.inserted_id:  # Check if insertion failed
            return jsonify({"error": "Failed to insert supplement"}), 500
        
        # Return the newly created document's _id
        return jsonify({"message": "Supplement created successfully", "_id": str(result.inserted_id)}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


@bp.route('/<string:supplement_id>', methods=['PUT'])
@jwt_required()
def update_supplement(supplement_id):
    """Update an existing supplement"""
    try:
        _id = ObjectId(supplement_id)  # Convert the string ID to ObjectId
        supplement_data = request.json
        Supplement.update(_id, supplement_data)
        return jsonify({"message": "Supplement updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


@bp.route('/<string:supplement_id>', methods=['DELETE'])
@jwt_required()
def delete_supplement(supplement_id):
    """Delete a supplement (soft delete by default)"""
    try:
        _id = ObjectId(supplement_id)  # Convert the string ID to ObjectId
        soft_delete = request.args.get('soft', 'true').lower() == 'true'  # Default to soft delete
        success = Supplement.delete(_id, soft_delete=soft_delete)
        if not success:
            return jsonify({"error": "Supplement not found"}), 404
        return jsonify({"message": "Supplement deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500
    
from flask import Blueprint, jsonify
from app.db.db import get_database as get_db
from bson.objectid import ObjectId

@bp.route('/by-supplement/<string:supplement_id>', methods=['GET'])
def get_interactions_by_supplement(supplement_id):
    """Get categorized interactions involving a specific supplement"""
    try:
        _id = ObjectId(supplement_id)
    except Exception:
        return jsonify({"error": "Invalid supplement ID format"}), 400

    try:
        db = get_db()

        # Query interactions where the supplement appears in the supplements array
        interactions_cursor = db.Interactions.find({
            "supplements": {
                "$elemMatch": {"supplementId": str(_id)}
            }
        })

        # Categorize interactions
        supplement_supplement = []
        supplement_food = []

        for interaction in interactions_cursor:
            interaction["_id"] = str(interaction["_id"])  # serialize ObjectId

            if interaction.get("interactionType") == "Supplement-Supplement":
                supplement_supplement.append(interaction)
            elif interaction.get("interactionType") == "Supplement-Food":
                supplement_food.append(interaction)

        return jsonify({
            "supplementSupplementInteractions": supplement_supplement,
            "supplementFoodInteractions": supplement_food
        }), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching interactions", "details": str(e)}), 500