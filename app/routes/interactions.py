from flask import Blueprint, jsonify, request
from app.models.interaction import Interaction
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.auth import admin_required
from app.models.user import User
from bson.objectid import ObjectId

# Create the blueprint
bp = Blueprint('interactions', __name__, url_prefix='/api/interactions')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_interactions():
    """Get a list of interactions"""
    try:
        # Get query parameters
        interaction_type = request.args.get('type')
        severity = request.args.get('severity')
        search_query = request.args.get('query', '')
        
        # Build query
        query = {}
        
        if interaction_type:
            query['interactionType'] = interaction_type
            
        if severity:
            query['severity'] = severity
            
        if search_query:
            # Search in effect, description, and recommendation fields
            query['$or'] = [
                {'effect': {'$regex': search_query, '$options': 'i'}},
                {'description': {'$regex': search_query, '$options': 'i'}},
                {'recommendation': {'$regex': search_query, '$options': 'i'}}
            ]
            
        # Get interactions
        interactions = Interaction.find_all(query)
        
        # Return interactions
        return jsonify([i.to_dict() for i in interactions]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to get interactions", "details": str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_interaction():
    """Create a new interaction (admin only)"""
    try:
        # Check for JSON content
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
            
        # Get data
        data = request.json
        
        # Create interaction
        interaction = Interaction.create(data)
        
        # Return response
        return jsonify({
            "message": "Interaction created successfully",
            "_id": str(interaction._id) if interaction._id else None
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to create interaction", "details": str(e)}), 500

@bp.route('/<interaction_id>', methods=['GET'])
@jwt_required()
def get_interaction(interaction_id):
    """Get a specific interaction by ID"""
    try:
        # Get interaction
        interaction = Interaction.find_by_id(interaction_id)
        
        if not interaction:
            return jsonify({"error": "Interaction not found"}), 404
            
        # Return interaction
        return jsonify(interaction.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to get interaction", "details": str(e)}), 500

@bp.route('/<interaction_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_interaction(interaction_id):
    """Update an interaction (admin only)"""
    try:
        # Check for JSON content
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
            
        # Get data
        data = request.json
        
        if not data:
            return jsonify({"error": "No update data provided"}), 400
            
        # Update interaction
        interaction = Interaction.update(interaction_id, data)
        
        # Return response
        return jsonify({
            "message": "Interaction updated successfully",
            "_id": str(interaction._id) if interaction._id else None
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to update interaction", "details": str(e)}), 500

@bp.route('/<interaction_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_interaction(interaction_id):
    """Delete an interaction (admin only)"""
    try:
        # Get soft delete parameter
        soft_delete = request.args.get('soft', 'true').lower() == 'true'
        
        # Delete interaction
        interaction = Interaction.delete(interaction_id, soft_delete=soft_delete)
        
        if not interaction:
            return jsonify({"error": "Interaction not found"}), 404
            
        # Return response
        return jsonify({
            "message": "Interaction deleted successfully",
            "_id": str(interaction._id) if interaction._id else None
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to delete interaction", "details": str(e)}), 500

@bp.route('/check', methods=['POST'])
@jwt_required()
def check_interactions():
    """Check for interactions between supplements, food items, and medications"""
    try:
        # Check for JSON content
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
            
        # Get data
        data = request.json
        
        # Get parameters
        supplement_ids = data.get('supplementIds', [])
        food_items = data.get('foodItems', [])
        medications = data.get('medications', [])
        
        # Check for required parameters
        if not supplement_ids:
            return jsonify({"error": "At least one supplement ID is required"}), 400
            
        # Check interactions
        interactions = Interaction.check_interactions(
            supplement_ids=supplement_ids,
            food_items=food_items,
            medications=medications
        )
        
        # Return interactions
        return jsonify({
            "interactions": [i.to_dict() for i in interactions],
            "count": len(interactions)
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to check interactions", "details": str(e)}), 500
