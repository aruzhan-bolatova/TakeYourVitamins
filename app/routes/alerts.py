from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db.db import get_database as get_db
from bson.objectid import ObjectId
from datetime import datetime

# Create the blueprint
bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get a list of alerts for the current user"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get database connection
        db = get_db()
        
        # Get query parameters for filtering
        read = request.args.get('read')
        
        # Build query
        query = {'userId': user_id}
        if read is not None:
            query['read'] = read.lower() == 'true'
        
        # Find alerts for this user
        alerts = list(db.Alerts.find(query))
        
        # Convert ObjectId to string for JSON serialization
        for alert in alerts:
            if '_id' in alert:
                alert['_id'] = str(alert['_id'])
        
        return jsonify(alerts), 200
    except Exception as e:
        return jsonify({"error": "Failed to get alerts", "details": str(e)}), 500

@bp.route('/<alert_id>', methods=['PUT'])
@jwt_required()
def mark_alert_read(alert_id):
    """Mark an alert as read"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get database connection
        db = get_db()
        
        # Get JSON data
        data = request.json or {}
        read = data.get('read', True)
        
        # Try to parse alert_id as ObjectId
        try:
            obj_id = ObjectId(alert_id)
            id_query = {'_id': obj_id}
        except:
            # If not a valid ObjectId, try using it as is
            id_query = {'alertId': alert_id}
        
        # Update the alert
        result = db.Alerts.update_one(
            {**id_query, 'userId': user_id},
            {'$set': {'read': read, 'updatedAt': datetime.utcnow().isoformat()}}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Alert not found"}), 404
            
        return jsonify({"message": "Alert updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to update alert", "details": str(e)}), 500

@bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_test_alert():
    """Generate a test alert for the current user (for development only)"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get database connection
        db = get_db()
        
        # Create a test alert
        new_alert = {
            'alertId': f"ALERT{datetime.utcnow().timestamp()}",
            'userId': user_id,
            'type': 'interaction',
            'title': 'Potential Supplement Interaction',
            'message': 'We detected a potential interaction between your supplements.',
            'severity': 'medium',
            'read': False,
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': None
        }
        
        # Insert the alert
        result = db.Alerts.insert_one(new_alert)
        
        # Return the new alert with string ID
        new_alert['_id'] = str(result.inserted_id)
        
        return jsonify(new_alert), 201
    except Exception as e:
        return jsonify({"error": "Failed to generate test alert", "details": str(e)}), 500
