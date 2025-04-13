from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

# Create the blueprint
bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get the current user's profile"""
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "userId": user.user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "gender": user.gender
    }), 200

@bp.route('/', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Update the current user's profile"""
    # For now, this is a placeholder
    return jsonify({"message": "Profile update functionality coming soon"}), 501
