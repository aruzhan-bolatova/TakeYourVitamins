'''
GET http://10.228.244.25:5001/api/auth/me
POST http://10.228.244.25:5001/api/auth/register
POST http://10.228.244.25:5001/api/auth/login
POST http://10.228.244.25:5001/api/auth/logout
'''
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity, 
                               get_jwt, current_user)
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
import datetime
from bson.objectid import ObjectId  # Import ObjectId to handle MongoDB _id

# Create the blueprint
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Missing JSON in request"}), 400
    except Exception:
        return jsonify({"error": "Invalid JSON format"}), 400
    
    # Validate required fields
    required_fields = ['name', 'email', 'password', 'age', 'gender']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        # Create the user
        user = User.create(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            age=data['age'],
            gender=data['gender']
        )
        
        # Generate access token
        access_token = create_access_token(
            identity=str(user._id),
            expires_delta=datetime.timedelta(hours=1)
        )
        
        return jsonify({
            "message": "User registered successfully",
            "_id": str(user._id),
            "access_token": access_token
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to register user", "details": str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return a JWT token"""
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Missing JSON in request"}), 400
    except Exception:
        return jsonify({"error": "Invalid JSON format"}), 400
    
    # Validate required fields
    if 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Authenticate user
    user = User.authenticate(data['email'], data['password'])
    
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Generate access token
    access_token = create_access_token(
        identity=str(user._id),
        expires_delta=datetime.timedelta(hours=1)
    )
    
    return jsonify({
        "message": "Login successful",
        "_id": str(user._id),
        "access_token": access_token
    }), 200

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout a user by blacklisting their current token"""
    jti = get_jwt()["jti"]
    user_id = get_jwt_identity()
    
    # Get token expiration time from JWT
    token_exp = get_jwt()["exp"]
    expires_at = datetime.datetime.fromtimestamp(token_exp, tz=datetime.timezone.utc)
    
    # Add token to blacklist
    try:
        TokenBlacklist.add_to_blacklist(
            jti=jti,
            token_type="access",
            user_id=user_id,
            expires_at=expires_at
        )
    except Exception:
        # Still return success even if blacklisting fails
        # This is a security best practice - not telling the user about internal issues
        pass
    
    return jsonify({"message": "Successfully logged out"}), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get the current authenticated user's details"""
    user_id = get_jwt_identity()
    print(f"User ID from JWT: {user_id}")
    
    user_id = ObjectId(user_id)
    user = User.find_by_id(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "_id": str(user._id),
        "userId": user.user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "gender": user.gender
    }), 200
