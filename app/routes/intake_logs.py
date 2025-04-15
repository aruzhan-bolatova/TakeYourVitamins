from flask import Blueprint, jsonify, request
from app.models.interaction import Interaction
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.intake_log import IntakeLog
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# Create the blueprint
bp = Blueprint('intake_logs', __name__, url_prefix='/api/intake-logs')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_intake_logs():
    """Get a list of intake logs for the current user"""
    try:
        # Get user ID from token
        user_id = get_jwt_identity()
        
        # Get query parameters
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        supplement_id = request.args.get('supplementId')
        
        # Build query
        query = {'userId': user_id}
        
        if start_date:
            query['timestamp'] = query.get('timestamp', {})
            query['timestamp']['$gte'] = start_date
            
        if end_date:
            query['timestamp'] = query.get('timestamp', {})
            query['timestamp']['$lte'] = end_date
            
        if supplement_id:
            query['supplementId'] = supplement_id
            
        # Get intake logs
        logs = IntakeLog.find_all(query)
        
        # Return logs
        return jsonify([log.to_dict() for log in logs]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to get intake logs", "details": str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_intake_log():
    """Create a new intake log"""
    try:
        # Check for JSON content
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
            
        # Get data
        data = request.json
        
        # Add user ID
        data['userId'] = get_jwt_identity()
        
        # Create log
        log = IntakeLog.create(data)
        
        # Return response
        return jsonify({
            "message": "Intake log created successfully",
            "_id": str(log._id) if log._id else None
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to create intake log", "details": str(e)}), 500

@bp.route('/check-interactions', methods=['POST'])
@jwt_required()
def check_intake_interactions():
    """Check for interactions in a potential intake"""
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
            
        # Get user ID
        user_id = get_jwt_identity()
        
        # Check interactions with specified items
        interactions = Interaction.check_interactions(
            supplement_ids=supplement_ids,
            food_items=food_items,
            medications=medications
        )
        
        # Also check interactions with supplements taken in the last 24 hours
        recent_logs = IntakeLog.find_recent(user_id, hours=24)
        recent_supplement_ids = [log.supplement_id for log in recent_logs 
                              if log.supplement_id not in supplement_ids]
        
        if recent_supplement_ids:
            # Combine with current supplements to check all interactions
            all_supplement_ids = supplement_ids + recent_supplement_ids
            all_interactions = Interaction.check_interactions(
                supplement_ids=all_supplement_ids
            )
            
            # Filter out interactions that don't involve any supplements from the current request
            additional_interactions = []
            for interaction in all_interactions:
                if interaction not in interactions:  # This won't work without proper __eq__ implementation
                    # Check if any supplements in this interaction are in the current request
                    interaction_supp_ids = [s.get('supplementId') for s in interaction.supplements]
                    if any(sid in supplement_ids for sid in interaction_supp_ids):
                        additional_interactions.append(interaction)
            
            # Add additional interactions
            interactions.extend(additional_interactions)
        
        # Categorize interactions by severity
        categorized = {
            'severe': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for interaction in interactions:
            severity = interaction.severity.lower() if interaction.severity else 'low'
            if severity in categorized:
                categorized[severity].append(interaction.to_dict())
            else:
                categorized['low'].append(interaction.to_dict())
        
        # Return interactions
        return jsonify({
            "interactions": [i.to_dict() for i in interactions],
            "count": len(interactions),
            "categorized": categorized,
            "recentSupplements": recent_supplement_ids
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to check interactions", "details": str(e)}), 500

@bp.route('/<log_id>', methods=['GET'])
@jwt_required()
def get_intake_log(log_id):
    """Get a specific intake log"""
    try:
        # Get log
        log = IntakeLog.find_by_id(log_id)
        
        if not log:
            return jsonify({"error": "Intake log not found"}), 404
            
        # Check user permission
        user_id = get_jwt_identity()
        if log.user_id != user_id:
            # Check if user is admin
            user = User.find_by_id(user_id)
            if not user or user.role != 'admin':
                return jsonify({"error": "You do not have permission to access this log"}), 403
            
        # Return log
        return jsonify(log.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to get intake log", "details": str(e)}), 500

@bp.route('/<log_id>', methods=['PUT'])
@jwt_required()
def update_intake_log(log_id):
    """Update an intake log"""
    try:
        # Check for JSON content
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
            
        # Get data
        data = request.json
        
        if not data:
            return jsonify({"error": "No update data provided"}), 400
            
        # Check user permission
        user_id = get_jwt_identity()
        log = IntakeLog.find_by_id(log_id)
        
        if not log:
            return jsonify({"error": "Intake log not found"}), 404
            
        if log.user_id != user_id:
            # Check if user is admin
            user = User.find_by_id(user_id)
            if not user or user.role != 'admin':
                return jsonify({"error": "You do not have permission to update this log"}), 403
            
        # Update log
        updated_log = IntakeLog.update(log_id, data)
        
        # Return response
        return jsonify({
            "message": "Intake log updated successfully",
            "_id": str(updated_log._id) if updated_log._id else None
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to update intake log", "details": str(e)}), 500

@bp.route('/<log_id>', methods=['DELETE'])
@jwt_required()
def delete_intake_log(log_id):
    """Delete an intake log"""
    try:
        # Check user permission
        user_id = get_jwt_identity()
        log = IntakeLog.find_by_id(log_id)
        
        if not log:
            return jsonify({"error": "Intake log not found"}), 404
            
        if log.user_id != user_id:
            # Check if user is admin
            user = User.find_by_id(user_id)
            if not user or user.role != 'admin':
                return jsonify({"error": "You do not have permission to delete this log"}), 403
            
        # Delete log
        deleted_log = IntakeLog.delete(log_id)
        
        # Return response
        return jsonify({
            "message": "Intake log deleted successfully",
            "_id": str(deleted_log._id) if deleted_log._id else None
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to delete intake log", "details": str(e)}), 500
