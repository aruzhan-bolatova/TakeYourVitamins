from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User


def admin_required(fn):
    """
    A decorator to protect a route with JWT and require admin role.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # First verify the JWT is valid
        verify_jwt_in_request()
        
        # Get the user ID from the JWT
        user_id = get_jwt_identity()
        
        # Find the user and check if they have the admin role
        user = User.find_by_id(user_id)
        if not user or user.role != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403
        
        # Call the original function
        return fn(*args, **kwargs)
    
    return wrapper


def check_user_access(fn):
    """
    A decorator to ensure users can only access their own resources.
    This middleware should be used on routes that include a :user_id parameter.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # First verify the JWT is valid
        verify_jwt_in_request()
        
        # Get the user ID from the JWT
        current_user_id = get_jwt_identity()
        
        # Get the user ID from the route parameter
        target_user_id = kwargs.get('user_id')
        
        # Get the current user to check role
        user = User.find_by_id(current_user_id)
        
        # Allow access if the user is accessing their own resource or if they're an admin
        if current_user_id == target_user_id or (user and user.role == 'admin'):
            return fn(*args, **kwargs)
        
        # Otherwise, deny access
        return jsonify({"error": "Access denied"}), 403
    
    return wrapper 