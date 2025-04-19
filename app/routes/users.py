'''
GET http://10.228.244.25:5001/api/users/
GET http://10.228.244.25:5001/api/users/6802e9cc0995ab3a4755f68d
PUT http://10.228.244.25:5001/api/users/6802e9cc0995ab3a4755f68d
    {
        "name": "John Doe"
    }
DELETE http://10.228.244.25:5001/api/users/6802e9cc0995ab3a4755f68d

'''
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.middleware.auth import check_user_access, admin_required
from app.db.db import get_database as get_db
from bson.objectid import ObjectId  # Import ObjectId to handle MongoDB _id

# Create the blueprint
bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_current_user_profile():
    """Get the current authenticated user's profile"""
    user_id = get_jwt_identity()
    print(f"User ID from JWT: {user_id}")
    # Convert the string ID to ObjectId
    user_id = ObjectId(user_id)
    user = User.find_by_id(user_id)
    print(f"User found: {user}")
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200


@bp.route('/<user_id>', methods=['GET'])
@jwt_required()
@check_user_access
def get_user_profile(user_id):
    """Get a specific user's profile"""
    # Convert the string ID to ObjectId
    try:
        user_id = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400
    # Find the user by ID
    user = User.find_by_id(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200


@bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
@check_user_access
def update_user_profile(user_id):
    """Update a user's profile"""
    data = request.get_json()

    # Validate input data
    if not data:
        return jsonify({"error": "No update data provided"}), 400
    
    try:
        
        user_id = ObjectId(user_id)
        # Update the user
        updated_user = User.update(user_id, data)
        
        if not updated_user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "message": "User updated successfully",
            "userId": updated_user.user_id,
            "name": updated_user.name,
            "email": updated_user.email,
            "age": updated_user.age,
            "gender": updated_user.gender,
            "role": updated_user.role
        }), 200
    except ValueError as e:
        # Handle validation errors
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": "Failed to update user", "details": str(e)}), 500


@bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
@check_user_access
def delete_user(user_id):
    """Soft delete a user"""
    # Convert the string ID to ObjectId
    try:
        user_id = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400
    # Delete the user
    deleted_user = User.delete(user_id)
    
    if not deleted_user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "message": "User deleted successfully",
        "_id": str(deleted_user._id),
    }), 200


# Admin only routes
@bp.route('/admin/all', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (admin only)"""
    db = get_db()
    users_data = list(db.Users.find({'deletedAt': None}))
    
    # Convert MongoDB objects to serializable format and remove sensitive fields
    users = []
    for user_data in users_data:
        user = {
            "_id": str(user_data['_id']),
            "userId": user_data.get('userId'),
            "name": user_data.get('name'),
            "email": user_data.get('email'),
            "age": user_data.get('age'),
            "gender": user_data.get('gender'),
            "role": user_data.get('role', 'user'),
            "createdAt": user_data.get('createdAt')
        }
        users.append(user)
    
    return jsonify({"users": users}), 200
