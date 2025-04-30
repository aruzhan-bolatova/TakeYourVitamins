from flask import Blueprint, jsonify, request
from app.models.symptom_log import SymptomLog
from app.db.db import get_database as get_db
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from datetime import datetime, UTC
from datetime import datetime, date, time as dtime

# Create the blueprint
bp = Blueprint('symptom_logs', __name__, url_prefix='/api/symptom-logs')


def validate_data(data):
    "Validate required fields and their formats."
    required_fields = ['symptom', 'date', 'time', 'rating']
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Missing or empty field: {field}")

    # Validate rating
    try:
        rating = int(data['rating'])
        if not (1 <= rating <= 10):
            raise ValueError("Rating must be an integer between 1 and 10")
    except ValueError:
        raise ValueError("Rating must be an integer between 1 and 10")

    # Validate date
    try:
        log_date = datetime.strptime(data['date'], "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format")

    # Validate time
    try:
        log_time = datetime.strptime(data['time'], "%H:%M").time()
    except ValueError:
        raise ValueError("Time must be in HH:MM format (24-hour)")

    now = datetime.now()
    today = now.date()
    current_time = now.time()

    # Check future date
    if log_date > today:
        raise ValueError("Invalid date: cannot be in the future")

    # Check future time for today
    if log_date == today and log_time > current_time:
        raise ValueError("Invalid time: cannot be in the future")


@bp.route('/', methods=['GET'])
# TESTING ON POSTMAN
# GET http://localhost:5001/api/symptom-logs/
# GET http://localhost:5001/api/symptom-logs/?dateFrom=2025-04-30&dateTo=2025-05-01
# GET http://localhost:5001/api/symptom-logs/?dateFrom=2025-04-30

@jwt_required()
def get_symptom_logs():
    """Get a list of symptom logs for the current user"""
    try:
        # Get user ID from token
        user_id = get_jwt_identity()
        
        # Get query parameters
        date_from = request.args.get('dateFrom', '')
        date_to = request.args.get('dateTo', None)  # Optional parameter
        
        # Get symptom logs
        if date_to:
            symptom_logs = SymptomLog.find_by_user(user_id, start_date=date_from, end_date=date_to)

        else:
            symptom_logs = SymptomLog.find_by_user(user_id, start_date=date_from)
        
        # Return logs
        return jsonify([log.to_dict() for log in symptom_logs]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to get symptom logs", "details": str(e)}), 500


@bp.route('/', methods=['POST'])
#TESTING ON POSTMAN
# POST to http://localhost:5000/api/symptom-logs/ with body format:
# {
#  "symptom": "Nausea",
#  "date": "2025-04-30",
#  "time": "16:00",
#  "rating": 3,
#  "notes": "Mild nausea after taking supplements"
# }
# Also tested with invalid date and time, and invalid rating (0 and 11)
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
            
        # Validate data
        validate_data(log_data)
        
        from datetime import datetime, UTC

        timestamp = str(datetime.now(UTC).timestamp()).replace('.', '')
        log_data['symptomLogId'] = f"SYMPTOM{timestamp}"
        log_data['logDate'] = f"{log_data['date']}T{log_data['time']}"
        log_data['createdAt'] = datetime.now(UTC).isoformat()
        log_data['updatedAt'] = None
        log_data['comments'] = log_data.get('notes')


        # Insert into database
        db = get_db()
        log_dict = SymptomLog(log_data).to_dict()
        result = db.SymptomLogs.insert_one(log_dict)
        
        if not result.inserted_id:
            return jsonify({"error": "Failed to insert symptom log"}), 500
            
        # Return response
        return jsonify({
            "message": "Symptom log created successfully",
            "log": {
                "symptomLogId": log_data["symptomLogId"],
                "symptom": log_data["symptom"],
                "logDate": log_data["logDate"],
                "rating": log_data["rating"],
                "comments": log_data.get("comments"),
                }
            }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to create symptom log", "details": str(e)}), 500

@bp.route('/<string:log_id>', methods=['PUT'])
# TESTING ON POSTMAN
# PUT to http://localhost:5000/api/symptom-logs/<log_id> with body format:
# {
#   "symptom": "Headache",
#   "rating": 10,
#   "date": "2025-04-30",
#   "time": "23:00",
#   "comments": "Increased intensity after screen time"
# }
# Also tested with invalid log_id (not found) and invalid data (missing fields/incorrect formats)
@jwt_required()
def update_symptom_log(log_id):
    try:
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        log_data = request.json
        if not log_data:
            return jsonify({"error": "No update data provided"}), 400

        validate_data(log_data)

        mongo_id = ObjectId(log_id)  # This is important
        user_id = get_jwt_identity()
        existing_log = SymptomLog.find_by_id(mongo_id)

        if not existing_log:
            return jsonify({"error": "Symptom log not found"}), 404
        if existing_log.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        success = SymptomLog.update(mongo_id, log_data)
        if not success:
            return jsonify({"error": "Failed to update symptom log"}), 500

        return jsonify({"message": "Symptom log updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to update symptom log", "details": str(e)}), 500


@bp.route('/<string:log_id>', methods=['DELETE'])
# TESTING ON POSTMAN
# DELETE http://localhost:5000/api/symptom-logs/<log_id>
# Tested with valid and invalid log_id (not found)
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
            # Check if user is authorized
            user = User.find_by_id(user_id)
            if not user:
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