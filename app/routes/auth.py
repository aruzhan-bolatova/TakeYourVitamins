from flask import Blueprint, request, jsonify
from app.models.user import User
from app.db.utils import generate_unique_id, hash_password
from flask_jwt_extended import create_access_token
from datetime import datetime, UTC

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.find_by_email(data['email']):
        return jsonify({'error': 'Email already exists'}), 400
        
    try:
        user_id = generate_unique_id('USER')
        user_data = User.create(
            userId=user_id,
            name=data['name'],
            email=data['email'],
            password=hash_password(data['password']),
            age=data['age'],
            gender=data['gender']
        )
        access_token = create_access_token(identity={'userId': user_data['userId'], 'email': user_data['email']})
        return jsonify({'userId': user_data['userId'], 'email': user_data['email'], 'token': access_token}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.find_by_email(data.get('email'))
    
    from app.db.utils import check_password
    if not user or not check_password(data.get('password'), user.get('password')):
        return jsonify({'error': 'Invalid credentials'}), 401
        
    access_token = create_access_token(identity={'userId': user['userId'], 'email': user['email']})
    return jsonify({'userId': user['userId'], 'token': access_token}), 200