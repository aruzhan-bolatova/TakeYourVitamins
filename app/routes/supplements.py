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
from app.models.intake_log import IntakeLog
# Import the database connection function
from app.db.db import get_database as get_db
from bson.objectid import ObjectId  # Import ObjectId to handle MongoDB _id
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
import math

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
    """Get a list of supplements with pagination and filtering"""
    try:
        # Get query parameters
        search_query = request.args.get('search', '')
        field = request.args.get('field', 'name')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        category = request.args.get('category', '')
        
        # Calculate skip value for pagination
        skip = (page - 1) * limit
        
        # Get supplements with pagination
        db = get_db()
        
        # Build query
        query = {}
        
        # Add search if provided
        if search_query:
            query[field] = {'$regex': search_query, '$options': 'i'}
            
        # Add category filter if provided
        if category:
            query['category'] = {'$regex': category, '$options': 'i'}
            
        # Exclude soft-deleted supplements
        query['deletedAt'] = {'$exists': False}
        
        # Get total count for pagination
        total_count = db.Supplements.count_documents(query)
        
        # Get supplements with pagination
        supplements_data = db.Supplements.find(query).skip(skip).limit(limit)
        supplements = [Supplement(s).to_dict() for s in supplements_data]
        
        # Calculate pagination information
        total_pages = math.ceil(total_count / limit)
        has_next = page < total_pages
        has_prev = page > 1
        
        # Return supplements with pagination info
        return jsonify({
            "supplements": supplements,
            "pagination": {
                "page": page,
                "limit": limit,
                "totalItems": total_count,
                "totalPages": total_pages,
                "hasNext": has_next,
                "hasPrev": has_prev
            }
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to get supplements", "details": str(e)}), 500


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
@jwt_required()
def create_supplement():
    """Create a new supplement (admin only)"""
    try:
        # Get user ID and check if admin
        user_id = get_jwt_identity()
        if not admin_required(user_id):
            return jsonify({"error": "Admin privileges required to create supplements"}), 403
            
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
@jwt_required()
def update_supplement(supplement_id):
    """Update an existing supplement (admin only)"""
    try:
        # Get user ID and check if admin
        user_id = get_jwt_identity()
        if not admin_required(user_id):
            return jsonify({"error": "Admin privileges required to update supplements"}), 403
            
        # Validate request has JSON content
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
            
        # Get update data
        supplement_data = request.json
        
        if not supplement_data:
            return jsonify({"error": "No update data provided"}), 400
            
        _id = ObjectId(supplement_id)  # Convert the string ID to ObjectId
        Supplement.update(_id, supplement_data)
        return jsonify({"message": "Supplement updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


@bp.route('/<string:supplement_id>', methods=['DELETE'])
@jwt_required()
def delete_supplement(supplement_id):
    """Delete a supplement (admin only, soft delete by default)"""
    try:
        # Get user ID and check if admin
        user_id = get_jwt_identity()
        if not admin_required(user_id):
            return jsonify({"error": "Admin privileges required to delete supplements"}), 403
            
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

@bp.route('/search', methods=['GET'])
def search_supplements():
    """Search supplements by name, aliases, or description"""
    try:
        # Get query parameters
        query = request.args.get('q', '')
        if not query:
            return jsonify({"error": "Search query (q) is required"}), 400
            
        # Get database connection
        db = get_db()
        
        # Build search query using regex to match name, aliases, or description
        search_query = {
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'aliases': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}}
            ],
            'deletedAt': {'$exists': False}  # Exclude deleted supplements
        }
        
        # Get matching supplements
        supplements_data = db.Supplements.find(search_query).limit(20)  # Limit to 20 results
        supplements = [Supplement(s).to_dict() for s in supplements_data]
        
        # Return search results
        return jsonify({
            "query": query,
            "results": supplements,
            "count": len(supplements)
        }), 200
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

@bp.route('/autocomplete', methods=['GET'])
def autocomplete_supplements():
    """Autocomplete supplement names"""
    try:
        # Get query parameters
        query = request.args.get('q', '')
        if not query:
            return jsonify({"error": "Search query (q) is required"}), 400
            
        # Get database connection
        db = get_db()
        
        # Build autocomplete query - match the beginning of names or aliases
        autocomplete_query = {
            '$or': [
                {'name': {'$regex': f'^{query}', '$options': 'i'}},  # Starts with query
                {'aliases': {'$regex': f'^{query}', '$options': 'i'}}  # Alias starts with query
            ],
            'deletedAt': {'$exists': False}  # Exclude deleted supplements
        }
        
        # Get matching supplements - project only the necessary fields
        projection = {'_id': 1, 'supplementId': 1, 'name': 1, 'aliases': 1, 'category': 1}
        supplements_data = db.Supplements.find(autocomplete_query, projection).limit(10)
        
        # Format for autocomplete
        autocomplete_results = []
        for s in supplements_data:
            autocomplete_results.append({
                "id": str(s.get('_id')),
                "supplementId": s.get('supplementId'),
                "name": s.get('name'),
                "aliases": s.get('aliases', []),
                "category": s.get('category', '')
            })
        
        # Return autocomplete results
        return jsonify({
            "query": query,
            "results": autocomplete_results,
            "count": len(autocomplete_results)
        }), 200
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

@bp.route('/<string:supplement_id>/intakelogs', methods=['GET'])
@jwt_required()
def get_supplement_intake_logs(supplement_id):
    """Get intake logs for a specific supplement"""
    try:
        # Validate the supplement exists
        try:
            _id = ObjectId(supplement_id)
            supplement = Supplement.find_by_id(_id)
            if not supplement:
                return jsonify({"error": "Supplement not found"}), 404
        except Exception:
            return jsonify({"error": "Invalid supplement ID format"}), 400
        
        # Get user ID from token
        user_id = get_jwt_identity()
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Check if admin - admins can view all logs
        is_admin = admin_required(user_id)
        
        # Build query
        db = get_db()
        query = {'supplementId': str(_id), 'isDeleted': {'$ne': True}}
        
        # If not admin, restrict to current user's logs
        if not is_admin:
            query['userId'] = user_id
        
        # Get total count for pagination
        total_count = db.IntakeLogs.count_documents(query)
        
        # Get intake logs
        logs_data = db.IntakeLogs.find(query).sort('timestamp', -1).skip(skip).limit(limit)
        logs = [IntakeLog(log).to_dict() for log in logs_data]
        
        # Calculate pagination information
        total_pages = math.ceil(total_count / limit)
        has_next = page < total_pages
        has_prev = page > 1
        
        # Return intake logs with pagination info
        return jsonify({
            "supplementId": str(_id),
            "supplementName": supplement.name,
            "logs": logs,
            "pagination": {
                "page": page,
                "limit": limit,
                "totalItems": total_count,
                "totalPages": total_pages,
                "hasNext": has_next,
                "hasPrev": has_prev
            }
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500