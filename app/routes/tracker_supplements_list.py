'''
1. GET /api/tracker_supplements_list/ 
    find the tracker_supplement_list for user, if not found, create a new one
2. POST /api/tracker_supplements_list/
    create a new tracker_supplement_list for user, only one tracker_supplement_list per user
3. POST /api/tracker_supplements_list/<user_id>
    add a tracked_supplement to the user's tracker_supplement_list
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
import interactions

# Create the blueprint
bp = Blueprint('tracker_supplements_list', __name__, url_prefix='/api/tracker_supplements_list')

# # Helper function to check admin privileges
# def is_admin(user_id):
#     """Check if user has admin role"""
#     user = User.find_by_id(user_id)
#     if not user or user.role != 'admin':
#         return False
#     return True

@bp.route('/', methods=['GET'])
@jwt_required()
def get_user_tracker_supplement_list():
    """
    Get the TrackerSupplementList for the current user by user_id
    and return a JSON response of all TrackedSupplement in the list.
    """
    try:
        # Get the user ID from the JWT token
        user_id = get_jwt_identity()

        # Find the TrackerSupplementList for the user
        tracker_supplement_list = TrackerSupplementList.find_by_user_id(user_id)
        if not tracker_supplement_list:
            return jsonify({"error": "TrackerSupplementList not found for the user"}), 404

        # Convert all tracked supplements to dictionaries
        tracked_supplements = [
            supplement.to_dict() for supplement in tracker_supplement_list.tracked_supplements
        ]

        # Return the tracked supplements as a JSON response
        return jsonify({"trackedSupplements": tracked_supplements}), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve TrackerSupplementList", "details": str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_tracker_supplement_list():
    """
    Create a new TrackerSupplementList for the current user.
    """
    try:
        # Get the user ID from the JWT token
        user_id = get_jwt_identity()

        # Check if a TrackerSupplementList already exists for the user
        existing_list = TrackerSupplementList.find_by_user_id(user_id)
        if existing_list:
            # If the list already exists, do nothing and return a success message
            return jsonify({"message": "TrackerSupplementList already exists for this user", "_id": str(existing_list._id)}), 200

        # Create a new TrackerSupplementList
        tracker_supplement_list = TrackerSupplementList.create(user_id)

        # Return the created TrackerSupplementList as a JSON response
        return jsonify({"message": "TrackerSupplementList created successfully", "_id": str(tracker_supplement_list._id)}), 201

    except Exception as e:
        return jsonify({"error": "Failed to create TrackerSupplementList", "details": str(e)}), 500


@bp.route('/<string:user_id>', methods=['POST'])
@jwt_required()
def add_tracked_supplement():
    """
    Add a tracked supplement to the user's TrackerSupplementList.
    """
    try:
        # Get the user ID from the JWT token
        current_user_id = get_jwt_identity()

        # Get the tracked supplement data from the request
        tracked_supplement_data = request.json
        if not tracked_supplement_data:
            return jsonify({"error": "Missing tracked supplement data"}), 400

        # Add the tracked supplement to the user's TrackerSupplementList
        tracker_supplement_list = TrackerSupplementList.add_tracked_supplement(current_user_id, tracked_supplement_data)

        if not tracker_supplement_list:
            return jsonify({"error": "Failed to add tracked supplement"}), 500

        # Return the updated TrackerSupplementList as a JSON response
        return jsonify({"message": "Tracked supplement added successfully", "_id": str(tracker_supplement_list._id)}), 200

    except Exception as e:
        return jsonify({"error": "Failed to add tracked supplement", "details": str(e)}), 500


@bp.route('/<string:user_id>', methods=['PUT'])
@jwt_required()
def update_tracked_supplement():
    """
    Update a tracked supplement in the user's TrackerSupplementList.
    """
    try:
        # Get the user ID from the JWT token
        current_user_id = get_jwt_identity()

        # Get the tracked supplement data from the request
        tracked_supplement_data = request.json
        if not tracked_supplement_data:
            return jsonify({"error": "Missing tracked supplement data"}), 400

        # Update the tracked supplement in the user's TrackerSupplementList
        tracker_supplement_list = TrackerSupplementList.update_tracked_supplement(current_user_id, tracked_supplement_data)

        if not tracker_supplement_list:
            return jsonify({"error": "Failed to update tracked supplement"}), 500

        # Return the updated TrackerSupplementList as a JSON response
        return jsonify({"message": "Tracked supplement updated successfully", "_id": str(tracker_supplement_list._id)}), 200

    except Exception as e:
        return jsonify({"error": "Failed to update tracked supplement", "details": str(e)}), 500

@bp.route('/<string:user_id>', methods=['DELETE'])
@jwt_required()
def delete_tracked_supplement():
    """
    Delete a tracked supplement from the user's TrackerSupplementList.
    """
    try:
        # Get the user ID from the JWT token
        current_user_id = get_jwt_identity()

        # Get the tracked supplement ID from the request
        tracked_supplement_id = request.json.get('trackedSupplementId')
        if not tracked_supplement_id:
            return jsonify({"error": "Missing tracked supplement ID"}), 400

        # Delete the tracked supplement from the user's TrackerSupplementList
        tracker_supplement_list = TrackerSupplementList.delete_tracked_supplement(current_user_id, tracked_supplement_id)

        if not tracker_supplement_list:
            return jsonify({"error": "Failed to delete tracked supplement"}), 500

        # Return the updated TrackerSupplementList as a JSON response
        return jsonify({"message": "Tracked supplement deleted successfully", "_id": str(tracker_supplement_list._id)}), 200

    except Exception as e:
        return jsonify({"error": "Failed to delete tracked supplement", "details": str(e)}), 500

@bp.route('/<string:user_id>', methods=['GET'])
@jwt_required()
def get_tracker_supplement_list_by_supplement_id():
    """
    Get the TrackerSupplementList for the current user by supplement ID.
    """
    try:
        # Get the user ID from the JWT token
        user_id = get_jwt_identity()

        # Get the supplement ID from the request
        supplement_id = request.args.get('supplementId')
        if not supplement_id:
            return jsonify({"error": "Missing supplement ID"}), 400

        # Find the TrackerSupplementList for the user
        tracker_supplement_list = TrackerSupplementList.find_by_user_id(user_id)
        if not tracker_supplement_list:
            return jsonify({"error": "TrackerSupplementList not found for the user"}), 404

        # Find the tracked supplement by ID
        tracked_supplement = next((s for s in tracker_supplement_list.tracked_supplements if str(s._id) == supplement_id), None)
        if not tracked_supplement:
            return jsonify({"error": "Tracked supplement not found"}), 404

        # Return the tracked supplement as a JSON response
        return jsonify({"trackedSupplement": tracked_supplement.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve TrackerSupplementList", "details": str(e)}), 500




