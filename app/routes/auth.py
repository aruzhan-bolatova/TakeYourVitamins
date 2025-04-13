from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
import datetime

# Create the blueprint
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
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
            identity=user.user_id,
            expires_delta=datetime.timedelta(days=1)
        )
        
        return jsonify({
            "message": "User registered successfully",
            "userId": user.user_id,
            "access_token": access_token
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to register user", "details": str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return a JWT token"""
    data = request.get_json()
    
    # Validate required fields
    if 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Authenticate user
    user = User.authenticate(data['email'], data['password'])
    
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Generate access token
    access_token = create_access_token(
        identity=user.user_id,
        expires_delta=datetime.timedelta(days=1)
    )
    
    return jsonify({
        "message": "Login successful",
        "userId": user.user_id,
        "access_token": access_token
    }), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get the current authenticated user's details"""
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
