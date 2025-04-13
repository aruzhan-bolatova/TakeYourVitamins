from flask import Blueprint, request, jsonify
from app.models.intake_log import IntakeLog
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db.utils import generate_unique_id
from datetime import datetime, UTC

bp = Blueprint('intake_logs', __name__, url_prefix='/intake-logs')

@bp.route('/', methods=['POST'])
@jwt_required()
def log_intake():
    identity = get_jwt_identity()
    data = request.get_json()
    if identity['userId'] != data.get('userId'):
        return jsonify({'error': 'Forbidden'}), 403
    try:
        intake_log_id = generate_unique_id('INTAKE')
        intake_log = IntakeLog.create(
            intakeLogId=intake_log_id,
            userId=data['userId'],
            supplementId=data['supplementId'],
            intakeDate=data['intakeDate'],
            intakeTime=data['intakeTime'],
            dosage=data['dosage'],
            notes=data.get('notes')
        )
        # Convert MongoDB ObjectId to string
        if '_id' in intake_log:
            intake_log['_id'] = str(intake_log['_id'])
            
        # Trigger interaction check (implemented later)
        return jsonify({'intakeLogId': intake_log['intakeLogId']}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/', methods=['GET'])
@jwt_required()
def get_intake_logs():
    identity = get_jwt_identity()
    user_id = request.args.get('userId')
    if identity['userId'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403
        
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    
    if start_date and end_date:
        logs = list(IntakeLog.find_by_date_range(
            userId=user_id,
            start_date=start_date,
            end_date=end_date
        ))
    else:
        logs = list(IntakeLog.find_by_user_id(userId=user_id))
    
    # Convert MongoDB ObjectId to string
    for log in logs:
        if '_id' in log:
            log['_id'] = str(log['_id'])
            
    return jsonify(logs), 200