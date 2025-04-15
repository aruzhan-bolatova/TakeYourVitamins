''' 
Explanation of Endpoints
GET /api/supplements/:
    Retrieves a list of supplements.
    Supports optional search (?search=<query>), pagination (?page=<number>), and limit (?limit=<number>).
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
'''

from flask import Blueprint, jsonify, request
from app.models.supplement import Supplement
from app.models.interaction import Interaction
# Import the database connection function
from app.db.db import get_database as get_db
from bson.objectid import ObjectId  # Import ObjectId to handle MongoDB _id

# Create the blueprint
bp = Blueprint('supplements', __name__, url_prefix='/api/supplements')

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


@bp.route('/', methods=['POST'])
def create_supplement():
    """Create a new supplement"""
    try:
        # Validate request has JSON content
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
            
        supplement_data = request.json
        
        # Validate supplement data exists
        if not supplement_data:
            return jsonify({"error": "Empty supplement data"}), 400
            
        supplement = Supplement(supplement_data)
        supplement.validate_data(supplement_data)  # Validate the incoming data
        
        # Insert the supplement into the database
        db = get_db()
        supplement_dict = supplement.to_dict()
        result = db.Supplements.insert_one(supplement_dict)
        
        # Verify insertion was successful
        if not result.inserted_id:
            return jsonify({"error": "Failed to insert supplement"}), 500
            
        # Return the newly created document's _id
        response = {
            "message": "Supplement created successfully", 
            "_id": str(result.inserted_id)
        }
        return jsonify(response), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


@bp.route('/<string:supplement_id>', methods=['PUT'])
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

@bp.route('/<string:supplement_id>/interactions', methods=['GET'])
def get_supplement_interactions(supplement_id):
    """Get all interactions for a specific supplement"""
    try:
        # Validate the supplement exists
        try:
            _id = ObjectId(supplement_id)
            supplement = Supplement.find_by_id(_id)
            if not supplement:
                return jsonify({"error": "Supplement not found"}), 404
        except Exception:
            return jsonify({"error": "Invalid supplement ID format"}), 400
            
        # Get interactions
        interactions = Interaction.get_supplement_interactions(supplement_id)
        
        # Categorize interactions by type
        categorized = {
            'supplement': [],
            'food': [],
            'medication': []
        }
        
        for interaction in interactions:
            if interaction.interaction_type == 'Supplement-Supplement':
                categorized['supplement'].append(interaction.to_dict())
            elif interaction.interaction_type == 'Supplement-Food':
                categorized['food'].append(interaction.to_dict())
            elif interaction.interaction_type == 'Supplement-Medication':
                categorized['medication'].append(interaction.to_dict())
        
        # Return interactions
        return jsonify({
            "supplementId": supplement_id,
            "supplementName": supplement.name if hasattr(supplement, 'name') else "Unknown",
            "interactions": [i.to_dict() for i in interactions],
            "count": len(interactions),
            "categorized": categorized
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500