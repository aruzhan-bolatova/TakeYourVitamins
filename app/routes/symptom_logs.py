from flask import Blueprint, jsonify, request
from app.models.symptom_log import SymptomLog
from app.db.db import get_database as get_db
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

# Create the blueprint
bp = Blueprint('symptom_logs', __name__, url_prefix='/api/symptom-logs')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_symptom_logs():
    """Get a list of symptom logs for the current user"""
    try:
        # Get user ID from token
        user_id = get_jwt_identity()
        
        # Get query parameters
        date_from = request.args.get('dateFrom', '')
        date_to = request.args.get('dateTo', '')
        
        # Get symptom logs
        symptom_logs = SymptomLog.search(user_id=user_id, date_from=date_from, date_to=date_to)
        
        # Return logs
        return jsonify([log.to_dict() for log in symptom_logs]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to get symptom logs", "details": str(e)}), 500

@bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_symptom_logs():
    """Get all symptom logs (admin only)"""
    try:
        # Check if user is admin
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({"error": "You do not have permission to access all symptom logs"}), 403
        
        # Get query parameters
        user_id_param = request.args.get('userId', '')
        date_from = request.args.get('dateFrom', '')
        date_to = request.args.get('dateTo', '')
        
        # Get symptom logs
        symptom_logs = SymptomLog.search(
            user_id=user_id_param,
            date_from=date_from,
            date_to=date_to
        )
        
        # Return logs
        return jsonify([log.to_dict() for log in symptom_logs]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to get symptom logs", "details": str(e)}), 500

@bp.route('/<string:log_id>', methods=['GET'])
@jwt_required()
def get_symptom_log_by_id(log_id):
    """Get a specific symptom log by its ID"""
    try:
        # Convert the string ID to ObjectId
        _id = ObjectId(log_id)
        
        # Get log
        symptom_log = SymptomLog.find_by_id(_id)
        
        if not symptom_log:
            return jsonify({"error": "Symptom log not found"}), 404
            
        # Check user permission
        user_id = get_jwt_identity()
        if symptom_log.user_id != user_id:
            # Check if user is admin
            user = User.find_by_id(user_id)
            if not user or user.role != 'admin':
                return jsonify({"error": "You do not have permission to access this log"}), 403
        
        # Return log
        return jsonify(symptom_log.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to get symptom log", "details": str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_symptom_log():
    """Create a new symptom log"""
    try:
        # Check for JSON content
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
            
        # Get data
        log_data = request.json
        
        if not log_data:
            return jsonify({"error": "Empty symptom log data"}), 400
        
        # Add user ID from token
        log_data['userId'] = get_jwt_identity()
            
        # Create log
        symptom_log = SymptomLog(log_data)
        symptom_log.validate_data(log_data)
        
        # Insert into database
        db = get_db()
        log_dict = symptom_log.to_dict()
        result = db.SymptomLogs.insert_one(log_dict)
        
        if not result.inserted_id:
            return jsonify({"error": "Failed to insert symptom log"}), 500
            
        # Return response
        response = {
            "message": "Symptom log created successfully", 
            "_id": str(result.inserted_id)
        }
        return jsonify(response), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to create symptom log", "details": str(e)}), 500

@bp.route('/<string:log_id>', methods=['PUT'])
@jwt_required()
def update_symptom_log(log_id):
    """Update an existing symptom log"""
    try:
        # Check for JSON content
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
            
        # Get data
        log_data = request.json
        
        if not log_data:
            return jsonify({"error": "No update data provided"}), 400
            
        # Convert ID
        _id = ObjectId(log_id)
        
        # Check user permission
        user_id = get_jwt_identity()
        symptom_log = SymptomLog.find_by_id(_id)
        
        if not symptom_log:
            return jsonify({"error": "Symptom log not found"}), 404
            
        if symptom_log.user_id != user_id:
            # Check if user is admin
            user = User.find_by_id(user_id)
            if not user or user.role != 'admin':
                return jsonify({"error": "You do not have permission to update this log"}), 403
        
        # Update log
        success = SymptomLog.update(_id, log_data)
        
        if not success:
            return jsonify({"error": "Failed to update symptom log"}), 500
            
        # Return response
        return jsonify({
            "message": "Symptom log updated successfully",
            "_id": str(_id)
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to update symptom log", "details": str(e)}), 500

@bp.route('/<string:log_id>', methods=['DELETE'])
@jwt_required()
def delete_symptom_log(log_id):
    """Delete a symptom log (soft delete by default)"""
    try:
        # Convert ID
        _id = ObjectId(log_id)
        
        # Check user permission
        user_id = get_jwt_identity()
        symptom_log = SymptomLog.find_by_id(_id)
        
        if not symptom_log:
            return jsonify({"error": "Symptom log not found"}), 404
            
        if symptom_log.user_id != user_id:
            # Check if user is admin
            user = User.find_by_id(user_id)
            if not user or user.role != 'admin':
                return jsonify({"error": "You do not have permission to delete this log"}), 403
        
        # Get soft delete parameter (default to true)
        soft_delete = request.args.get('soft', 'true').lower() == 'true'
        
        # Delete log
        success = SymptomLog.delete(_id, soft_delete=soft_delete)
        
        if not success:
            return jsonify({"error": "Failed to delete symptom log"}), 500
            
        # Return response
        return jsonify({
            "message": "Symptom log deleted successfully",
            "_id": str(_id)
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to delete symptom log", "details": str(e)}), 500
