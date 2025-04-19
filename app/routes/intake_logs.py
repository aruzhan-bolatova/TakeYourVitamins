'''
POST http://10.228.244.25:5001/api/intake_logs/
    token required
    {
        "tracked_supplement_id": "680332671edd34b1c8995d4a", 
        "intake_date": "2025-04-19",
        "dosage_taken": 500,
        "unit": "mg",
        "notes": "Taken with breakfast"
        }
    output:
    {
        "_id": "680343bd87301efb7d3810b5", 
        "created_at": "2025-04-19T06:33:33.661289+00:00", 
        "deleted_at": null, 
        "dosage_taken": 500, 
        "intake_date": "2025-04-19", 
        "intake_time": "2025-04-19T06:33:33.661289+00:00", 
        "notes": "Taken with breakfast", 
        "supplement_name": "Vitamin C", 
        "tracked_supplement_id": "680332671edd34b1c8995d4a", 
        "unit": "mg", 
        "updated_at": "2025-04-19T06:33:33.661289+00:00", 
        "user_id": "67fffb85f1c67a82bcb6b42e"
        }

GET http://10.228.244.25:5001/api/intake_logs/
token required
    output:
    [
        {
            "_id": "680343bd87301efb7d3810b5", 
            "created_at": "2025-04-19T06:33:33.661289+00:00", 
            "deleted_at": null, 
            "dosage_taken": 500, 
            "intake_date": "2025-04-19", 
            "intake_time": "2025-04-19T06:33:33.661289+00:00", 
            "notes": "Taken with breakfast", 
            "supplement_name": "Vitamin C", 
            "tracked_supplement_id": "680332671edd34b1c8995d4a", 
            "unit": "mg", 
            "updated_at": "2025-04-19T06:33:33.661289+00:00", 
            "user_id": "67fffb85f1c67a82bcb6b42e"
        }
        ]
GET http://10.228.244.25:5001/api/intake_logs/today - get today's intake logs
token required


'''
from flask import Blueprint, request, jsonify, g
from app.models.intake_log import IntakeLog
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('intake_logs', __name__, url_prefix='/api/intake_logs')

@bp.route('/', methods=['POST'])
@jwt_required()
def create_intake_log():
    """
    Create a new supplement intake log.
    """
    try:
        user_id = get_jwt_identity()
        print(f"User ID from JWT: {user_id}")
        # Get data from request
        data = request.get_json()
        print(f"Data received: {data}")
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Validate required fields
        required_fields = ['tracked_supplement_id', 'intake_date', 'dosage_taken']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
                
        # Add user_id to the intake log data
        user_id = ObjectId(user_id)
        data['user_id'] = user_id
        
        # Create the intake log
        created_log = IntakeLog.create(data)
        return jsonify(created_log.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error creating intake log: {str(e)}"}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_intake_logs():
    """
    Get user's intake logs with optional filters.
    """
    try:
        user_id = get_jwt_identity()
        user_id = ObjectId(user_id)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        supplement_id = request.args.get('supplement_id')
        
        # Apply filters if provided
        if start_date and end_date:
            logs = IntakeLog.find_by_date_range(user_id, start_date, end_date)
        elif supplement_id:
            logs = IntakeLog.find_by_supplement_id(user_id, supplement_id)
        else:
            # Default to last 7 days if no filters
            today = datetime.now().strftime("%Y-%m-%d")
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            logs = IntakeLog.find_by_date_range(user_id, week_ago, today)
        
        return jsonify([log.to_dict() for log in logs]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error retrieving intake logs: {str(e)}"}), 500

@bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_intake_logs():
    """
    Get user's intake logs for today.
    """
    try:
        user_id = get_jwt_identity()
        user_id = ObjectId(user_id)
        today = datetime.now().strftime("%Y-%m-%d")
        logs = IntakeLog.find_by_date_range(user_id, today, today)
        return jsonify([log.to_dict() for log in logs]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error retrieving today's intake logs: {str(e)}"}), 500

@bp.route('/summary', methods=['GET'])
@jwt_required()
def get_intake_summary():
    """
    Get a summary of supplement intake over a time period.
    """
    try:
        user_id = get_jwt_identity()
        user_id = ObjectId(user_id)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
            
        summary = IntakeLog.get_intake_summary(user_id, start_date, end_date)
        return jsonify(summary), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error retrieving intake summary: {str(e)}"}), 500

@bp.route('/<log_id>', methods=['GET'])
@jwt_required()
def get_intake_log(log_id):
    """
    Get a specific intake log by ID.
    """
    try:
        user_id = get_jwt_identity()
        user_id = ObjectId(user_id)
        log = IntakeLog.find_by_id(log_id)
        if not log:
            return jsonify({"error": "Intake log not found"}), 404
            
        # Check if the log belongs to the current user
        if str(log.user_id) != str(user_id):
            return jsonify({"error": "Not authorized to access this intake log"}), 403
            
        return jsonify(log.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error retrieving intake log: {str(e)}"}), 500

@bp.route('/<log_id>', methods=['PUT'])
@jwt_required()
def update_intake_log(log_id):
    """
    Update an intake log.
    """
    try:
        user_id = get_jwt_identity()
        user_id = ObjectId(user_id)
        
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check if the log exists and belongs to the user
        log = IntakeLog.find_by_id(log_id)
        if not log:
            return jsonify({"error": "Intake log not found"}), 404
            
        if str(log.user_id) != str(user_id):
            return jsonify({"error": "Not authorized to update this intake log"}), 403
        
        # Update the log
        updated_log = IntakeLog.update(log_id, data)
        return jsonify(updated_log.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error updating intake log: {str(e)}"}), 500

@bp.route('/<log_id>', methods=['DELETE'])
@jwt_required()
def delete_intake_log(log_id):
    """
    Delete an intake log.
    """
    try:
        user_id = get_jwt_identity()
        user_id = ObjectId(user_id)
        # Check if the log exists and belongs to the user
        log = IntakeLog.find_by_id(log_id)
        if not log:
            return jsonify({"error": "Intake log not found"}), 404
            
        if str(log.user_id) != str(user_id):
            return jsonify({"error": "Not authorized to delete this intake log"}), 403
        
        # Delete the log
        IntakeLog.delete(log_id)
        return jsonify({"message": "Intake log deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error deleting intake log: {str(e)}"}), 500