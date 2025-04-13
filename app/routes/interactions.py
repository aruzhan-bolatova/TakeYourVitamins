from flask import Blueprint, request, jsonify
from app.models.interaction import Interaction
from app.models.supplement import Supplement
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, UTC
from app.db.utils import generate_unique_id

bp = Blueprint('interactions', __name__, url_prefix='/interactions')

@bp.route('/', methods=['GET'])
def get_interactions():
    """
    Get interactions for a supplement
    ---
    tags:
      - Interactions
    parameters:
      - in: query
        name: supplementId
        type: string
        required: false
        description: Filter interactions by supplement ID
    responses:
      200:
        description: List of interactions
      400:
        description: Invalid input
    """
    supplement_id = request.args.get('supplementId')
    limit = int(request.args.get('limit', 50))
    skip = int(request.args.get('skip', 0))
    
    if supplement_id:
        interactions = list(Interaction.find_by_supplement_id(
            supplementId=supplement_id,
            limit=limit,
            skip=skip
        ))
    else:
        # Fetch all interactions (with pagination)
        interactions = list(Interaction.find_by_interaction_type(
            interactionType=request.args.get('interactionType', ''),
            limit=limit,
            skip=skip
        ) if request.args.get('interactionType') else Interaction.get_collection().find({}, limit=limit, skip=skip))
    
    # Convert MongoDB ObjectId to string
    for interaction in interactions:
        if '_id' in interaction:
            interaction['_id'] = str(interaction['_id'])
    
    return jsonify(interactions), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def add_interaction():
    """
    Add a new interaction
    ---
    tags:
      - Interactions
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - supplementId1
            - interactionType
            - effect
            - description
            - severity
            - recommendation
          properties:
            supplementId1:
              type: string
            supplementId2:
              type: string
            foodItem:
              type: string
            interactionType:
              type: string
            effect:
              type: string
            description:
              type: string
            severity:
              type: string
            recommendation:
              type: string
            sources:
              type: array
              items:
                type: string
    responses:
      201:
        description: Interaction created
      400:
        description: Invalid input
      403:
        description: Admin access required
    """
    identity = get_jwt_identity()
    # Placeholder for role-based access; add role to User model and JWT identity if needed
    # if identity.get('role') != 'admin':
    #     return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    required_fields = ['supplementId1', 'interactionType', 'effect', 'description', 'severity', 'recommendation']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate supplementId1 exists
    if not Supplement.find_by_supplement_id(data['supplementId1']):
        return jsonify({'error': 'Supplement 1 not found'}), 404

    # Validate supplementId2 if provided
    if data.get('supplementId2') and not Supplement.find_by_supplement_id(data['supplementId2']):
        return jsonify({'error': 'Supplement 2 not found'}), 404

    # Either supplementId2 or foodItem must be provided, but not both
    if (data.get('supplementId2') and data.get('foodItem')) or (not data.get('supplementId2') and not data.get('foodItem')):
        return jsonify({'error': 'Must provide either supplementId2 or foodItem, but not both'}), 400

    interaction_id = generate_unique_id('INT')
    interaction = Interaction.create(
        interactionId=interaction_id,
        supplementId1=data['supplementId1'],
        interactionType=data['interactionType'],
        effect=data['effect'],
        description=data['description'],
        severity=data['severity'],
        recommendation=data['recommendation'],
        sources=data.get('sources', []),
        supplementId2=data.get('supplementId2'),
        foodItem=data.get('foodItem')
    )
    
    # Convert MongoDB ObjectId to string
    if '_id' in interaction:
        interaction['_id'] = str(interaction['_id'])
    
    return jsonify({'interactionId': interaction['interactionId'], 'supplementId1': interaction['supplementId1']}), 201

@bp.route('/<interaction_id>', methods=['PUT'])
@jwt_required()
def update_interaction(interaction_id):
    """
    Update an interaction
    ---
    tags:
      - Interactions
    parameters:
      - in: path
        name: interaction_id
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            supplementId1:
              type: string
            supplementId2:
              type: string
            foodItem:
              type: string
            interactionType:
              type: string
            effect:
              type: string
            description:
              type: string
            severity:
              type: string
            recommendation:
              type: string
            sources:
              type: array
              items:
                type: string
    responses:
      200:
        description: Interaction updated
      400:
        description: Invalid input
      403:
        description: Admin access required
      404:
        description: Interaction not found
    """
    identity = get_jwt_identity()
    # if identity.get('role') != 'admin':
    #     return jsonify({'error': 'Admin access required'}), 403

    interaction = Interaction.find_by_interaction_id(interaction_id)
    if not interaction:
        return jsonify({'error': 'Interaction not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    # Validate supplementId1 if provided
    if 'supplementId1' in data and not Supplement.find_by_supplement_id(data['supplementId1']):
        return jsonify({'error': 'Supplement 1 not found'}), 404

    # Validate supplementId2 if provided
    if 'supplementId2' in data and data['supplementId2'] and not Supplement.find_by_supplement_id(data['supplementId2']):
        return jsonify({'error': 'Supplement 2 not found'}), 404

    # Check for consistency between supplementId2 and foodItem
    if ('supplementId2' in data or 'foodItem' in data):
        new_supp2 = data.get('supplementId2', interaction.get('supplementId2'))
        new_food = data.get('foodItem', interaction.get('foodItem'))
        if (new_supp2 and new_food) or (not new_supp2 and not new_food):
            return jsonify({'error': 'Must provide either supplementId2 or foodItem, but not both'}), 400

    update_data = {}
    valid_fields = [
        'supplementId1', 'supplementId2', 'foodItem', 'interactionType', 
        'effect', 'description', 'severity', 'recommendation', 'sources'
    ]
    
    for field in valid_fields:
        if field in data:
            update_data[field] = data[field]
    
    Interaction.update(interaction_id, update_data)
    return jsonify({'interactionId': interaction_id, 'message': 'Interaction updated'}), 200

@bp.route('/<interaction_id>', methods=['DELETE'])
@jwt_required()
def delete_interaction(interaction_id):
    """
    Delete an interaction
    ---
    tags:
      - Interactions
    parameters:
      - in: path
        name: interaction_id
        type: string
        required: true
    responses:
      200:
        description: Interaction deleted
      403:
        description: Admin access required
      404:
        description: Interaction not found
    """
    identity = get_jwt_identity()
    # if identity.get('role') != 'admin':
    #     return jsonify({'error': 'Admin access required'}), 403

    interaction = Interaction.find_by_interaction_id(interaction_id)
    if not interaction:
        return jsonify({'error': 'Interaction not found'}), 404

    # Since the Interaction model may not have a delete method, we'll use the collection directly
    from app.db.db import get_collection
    get_collection('Interactions').delete_one({'interactionId': interaction_id})
    return jsonify({'message': 'Interaction deleted'}), 200