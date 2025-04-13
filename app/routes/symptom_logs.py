from flask import Blueprint, request, jsonify
from app.models.symptom_log import SymptomLog
from app.models.intake_log import IntakeLog
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, UTC
from app.db.utils import generate_unique_id

bp = Blueprint('symptom_logs', __name__, url_prefix='/symptom-logs')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_symptom_logs():
    """
    Get user's symptom logs
    ---
    tags:
      - Symptom Logs
    parameters:
      - in: query
        name: userId
        type: string
        required: true
        description: User ID to filter symptom logs
      - in: query
        name: startDate
        type: string
        required: false
        description: Start date for filtering (YYYY-MM-DD)
    responses:
      200:
        description: List of symptom logs
      403:
        description: Forbidden
      400:
        description: Invalid input
    """
    identity = get_jwt_identity()
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({'error': 'userId is required'}), 400
    if identity['userId'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403

    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    
    if start_date and end_date:
        logs = list(SymptomLog.find_by_date_range(userId=user_id, start_date=start_date, end_date=end_date))
    else:
        logs = list(SymptomLog.find_by_user_id(userId=user_id))
    
    # Convert MongoDB ObjectId to string
    for log in logs:
        if '_id' in log:
            log['_id'] = str(log['_id'])
            
    return jsonify(logs), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def log_symptom():
    """
    Log a symptom
    ---
    tags:
      - Symptom Logs
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - userId
            - symptom
            - rating
            - logDate
          properties:
            userId:
              type: string
            symptom:
              type: string
            rating:
              type: integer
            logDate:
              type: string
            comments:
              type: string
            intakeLogId:
              type: string
    responses:
      201:
        description: Symptom logged
      400:
        description: Invalid input
      403:
        description: Forbidden
      404:
        description: Intake log not found
    """
    identity = get_jwt_identity()
    data = request.get_json()
    if identity['userId'] != data.get('userId'):
        return jsonify({'error': 'Forbidden'}), 403

    required_fields = ['userId', 'symptom', 'rating', 'logDate']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate rating (e.g., between 1 and 5)
    if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400

    # Validate intakeLogId if provided
    if data.get('intakeLogId'):
        intake_log = IntakeLog.find_by_intake_log_id(data['intakeLogId'])
        if not intake_log or intake_log.get('userId') != data['userId'] or intake_log.get('isDeleted'):
            return jsonify({'error': 'Intake log not found or does not belong to user'}), 404

    symptom_log_id = generate_unique_id('SYMPTOM')
    symptom_log = SymptomLog.create(
        symptomLogId=symptom_log_id,
        userId=data['userId'],
        symptom=data['symptom'],
        rating=data['rating'],
        logDate=data['logDate'],
        comments=data.get('comments'),
        intakeLogId=data.get('intakeLogId')
    )
    
    # Convert MongoDB ObjectId to string
    if '_id' in symptom_log:
        symptom_log['_id'] = str(symptom_log['_id'])
    
    return jsonify({'symptomLogId': symptom_log['symptomLogId']}), 201

@bp.route('/<symptom_log_id>', methods=['PUT'])
@jwt_required()
def update_symptom_log(symptom_log_id):
    """
    Update a symptom log
    ---
    tags:
      - Symptom Logs
    parameters:
      - in: path
        name: symptom_log_id
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            symptom:
              type: string
            rating:
              type: integer
            logDate:
              type: string
            comments:
              type: string
            intakeLogId:
              type: string
    responses:
      200:
        description: Symptom log updated
      400:
        description: Invalid input
      403:
        description: Forbidden
      404:
        description: Symptom log not found
    """
    identity = get_jwt_identity()
    symptom_log = SymptomLog.find_by_symptom_log_id(symptom_log_id)
    if not symptom_log:
        return jsonify({'error': 'Symptom log not found'}), 404
    if identity['userId'] != symptom_log.get('userId'):
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    # Validate rating if provided
    if 'rating' in data:
        if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
            return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400

    # Validate intakeLogId if provided
    if 'intakeLogId' in data and data['intakeLogId']:
        intake_log = IntakeLog.find_by_intake_log_id(data['intakeLogId'])
        if not intake_log or intake_log.get('userId') != symptom_log.get('userId') or intake_log.get('isDeleted'):
            return jsonify({'error': 'Intake log not found or does not belong to user'}), 404

    update_data = {}
    for field in ['symptom', 'rating', 'logDate', 'comments', 'intakeLogId']:
        if field in data:
            update_data[field] = data[field]
    
    SymptomLog.update(symptom_log_id, update_data)
    return jsonify({'symptomLogId': symptom_log_id, 'message': 'Symptom log updated'}), 200

@bp.route('/<symptom_log_id>', methods=['DELETE'])
@jwt_required()
def delete_symptom_log(symptom_log_id):
    """
    Delete a symptom log
    ---
    tags:
      - Symptom Logs
    parameters:
      - in: path
        name: symptom_log_id
        type: string
        required: true
    responses:
      200:
        description: Symptom log deleted
      403:
        description: Forbidden
      404:
        description: Symptom log not found
    """
    identity = get_jwt_identity()
    symptom_log = SymptomLog.find_by_symptom_log_id(symptom_log_id)
    if not symptom_log:
        return jsonify({'error': 'Symptom log not found'}), 404
    if identity['userId'] != symptom_log.get('userId'):
        return jsonify({'error': 'Forbidden'}), 403

    # Since the SymptomLog model doesn't have a soft delete, we'll perform a hard delete
    from app.db.db import get_collection
    get_collection('SymptomLogs').delete_one({'symptomLogId': symptom_log_id})
    return jsonify({'message': 'Symptom log deleted'}), 200