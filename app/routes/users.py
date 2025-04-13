from flask import Blueprint, request, jsonify
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, UTC

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Get user profile
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
    responses:
      200:
        description: User profile
      403:
        description: Forbidden
      404:
        description: User not found
    """
    identity = get_jwt_identity()
    if identity['userId'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403

    user = User.find_by_user_id(user_id)
    if not user or user.get('deletedAt'):
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'userId': user['userId'],
        'name': user['name'],
        'email': user['email'],
        'age': user['age'],
        'gender': user['gender'],
        'createdAt': user['createdAt'],
        'updatedAt': user['updatedAt']
    }), 200

@bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Update user profile
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
            age:
              type: integer
            gender:
              type: string
    responses:
      200:
        description: User updated
      400:
        description: Invalid input
      403:
        description: Forbidden
      404:
        description: User not found
    """
    identity = get_jwt_identity()
    if identity['userId'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403

    user = User.find_by_user_id(user_id)
    if not user or user.get('deletedAt'):
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    # Validate email uniqueness if updated
    if 'email' in data and data['email'] != user['email']:
        if User.find_by_email(data['email']):
            return jsonify({'error': 'Email already exists'}), 400

    # Validate age if provided
    if 'age' in data and (not isinstance(data['age'], int) or data['age'] < 0):
        return jsonify({'error': 'Age must be a non-negative integer'}), 400

    update_data = {}
    if 'name' in data:
        update_data['name'] = data['name']
    if 'email' in data:
        update_data['email'] = data['email']
    if 'age' in data:
        update_data['age'] = data['age']
    if 'gender' in data:
        update_data['gender'] = data['gender']
    
    User.update(user_id, update_data)
    return jsonify({'userId': user_id, 'message': 'User updated'}), 200

@bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Delete user profile (soft delete)
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
    responses:
      200:
        description: User deleted
      403:
        description: Forbidden
      404:
        description: User not found
    """
    identity = get_jwt_identity()
    if identity['userId'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403

    user = User.find_by_user_id(user_id)
    if not user or user.get('deletedAt'):
        return jsonify({'error': 'User not found'}), 404

    User.soft_delete(user_id)
    return jsonify({'message': 'User deleted'}), 200