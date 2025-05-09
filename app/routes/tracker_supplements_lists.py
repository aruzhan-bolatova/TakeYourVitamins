'''
1. GET /api/tracker_supplements_list/ 
    find the tracker_supplement_list for user, if not found, create a new one
2. POST /api/tracker_supplements_list/
    create a new tracker_supplement_list for user, only one tracker_supplement_list per user
3. POST /api/tracker_supplements_list/<user_id>
    add a tracked_supplement to the user's tracker_supplement_list
    
    http://10.228.244.25:5001/api/tracker_supplements_list/67fffb85f1c67a82bcb6b42e
    {
        "supplementId": "67fe1342c0edae0f50b5737c",
        "supplementName": "Vitamin C",
        "dosage": 500,
        "unit": "mg",
        "frequency": "daily",
        "startDate": "2025-04-01T00:00:00Z",
        "endDate": "2025-05-01T00:00:00Z",
        "notes": "Take after meals"
    }
    
4. PUT /api/tracker_supplements_list/<user_id>
    update a tracked_supplement in the user's tracker_supplement_list
5. DELETE /api/tracker_supplements_list/<user_id>
    delete a tracked_supplement from the user's tracker_supplement_list
6. GET /api/tracker_supplements_list/<user_id>
    get the user's tracker_supplement_list by user_id

'''

from flask import Blueprint, jsonify, request
from app.models.tracker_supplement_list import TrackerSupplementList
from app.models.tracker_supplement_list import TrackedSupplement
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.auth import admin_required
from app.models.user import User
from bson.objectid import ObjectId

# Create the blueprint
bp = Blueprint('tracker_supplements_list', __name__, url_prefix='/api/tracker_supplements_list')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_or_create_user_tracker_supplement_list():
    """
    Find the TrackerSupplementList for the current user. If not found, create a new one.
    """
    try:
        user_id = get_jwt_identity()
        user_id = ObjectId(user_id)
        print(f"User ID received: {user_id}")

        # Find the TrackerSupplementList for the user
        tracker_supplement_list = TrackerSupplementList.find_by_user_id(user_id)
        print(f"TrackerSupplementList found: {tracker_supplement_list}")
        if not tracker_supplement_list:
            # Create a new list if not found
            tracker_supplement_list = TrackerSupplementList.create_for_user(user_id)
            print(f"New TrackerSupplementList created: {tracker_supplement_list}")

        return jsonify(tracker_supplement_list.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_tracker_supplement_list():
    """
    Create a new TrackerSupplementList for the current user.
    """
    try:
        user_id = get_jwt_identity()

        # Check if a TrackerSupplementList already exists for the user
        existing_list = TrackerSupplementList.find_by_user_id(user_id)
        if existing_list:
            return jsonify({"error": "TrackerSupplementList already exists for this user"}), 400

        # Create a new TrackerSupplementList
        tracker_supplement_list = TrackerSupplementList.create_for_user(user_id)
        return jsonify(tracker_supplement_list.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/<string:user_id>', methods=['POST'])
@jwt_required()
def add_tracked_supplement(user_id):
    """
    Add a tracked supplement to the user's TrackerSupplementList.
    """
    try:
        # Get the tracked supplement data from the request
        tracked_supplement_data = request.json
        if not tracked_supplement_data:
            return jsonify({"error": "Tracked supplement data is required"}), 400

        # Add the tracked supplement to the user's list
        updated_list = TrackerSupplementList.add_tracked_supplement(user_id, tracked_supplement_data)
        return jsonify(updated_list.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<string:user_id>', methods=['PUT'])
@jwt_required()
def update_tracked_supplement(user_id):
    """
    Update a tracked supplement in the user's TrackerSupplementList.
    """
    try:
        # Get the supplement ID and updated data from the request
        supplement_id = request.json.get('_id')
        updated_data = request.json
        if not supplement_id or not updated_data:
            return jsonify({"error": "Supplement ID and updated data are required"}), 400

        # Update the tracked supplement
        updated_list = TrackerSupplementList.update_tracked_supplement(user_id, supplement_id, updated_data)
        return jsonify(updated_list.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/<string:user_id>', methods=['DELETE'])
@jwt_required()
def delete_tracked_supplement(user_id):
    """
    Delete a tracked supplement from the user's TrackerSupplementList.
    """
    try:
        print(f"User ID received: {user_id}")
        
        # Get the supplement ID from the request
        supplement_id = request.json.get('_id')
        print(f"Supplement ID received: {supplement_id}")
        if not supplement_id:
            return jsonify({"error": "Supplement ID is required"}), 400

        # Delete the tracked supplement
        updated_list = TrackerSupplementList.delete_tracked_supplement(user_id, supplement_id)
        return jsonify("Tracked supplement deleted successfully",
                       updated_list.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/<string:user_id>', methods=['GET'])
@jwt_required()
def get_tracker_supplement_list_by_user_id(user_id):
    """
    Get the TrackerSupplementList for the specified user by user_id.
    """
    try:
        # Find the TrackerSupplementList for the user
        tracker_supplement_list = TrackerSupplementList.find_by_user_id(user_id)
        if not tracker_supplement_list:
            return jsonify({"error": "TrackerSupplementList not found for this user"}), 404

        return jsonify(tracker_supplement_list.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
