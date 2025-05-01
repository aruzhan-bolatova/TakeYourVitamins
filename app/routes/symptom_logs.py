from flask import Blueprint, request, jsonify, current_app
from app.models.symptom_log import SymptomLog, SymptomCategoryManager
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('symptom_logs', __name__, url_prefix='/api/symptom-logs')


@bp.before_app_first_request
def initialize_database():
    """Initialize database with symptom categories and symptoms"""
    try:
        SymptomCategoryManager.initialize_symptom_data()
        current_app.logger.info("Database initialized with symptom categories and symptoms")
    except Exception as e:
        current_app.logger.error(f"Error initializing database: {str(e)}")


@bp.route('/symptoms', methods=['GET'])
def get_all_symptoms():
    """Get all symptoms with their categories"""
    try:
        symptoms = SymptomLog.get_symptom_details()
        symptoms_list = list(symptoms.values())
        
        # Convert ObjectId to string for JSON serialization
        for symptom in symptoms_list:
            symptom["_id"] = str(symptom["_id"])
            symptom["categoryId"] = str(symptom["categoryId"])
            
        return jsonify({"symptoms": symptoms_list}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting symptoms: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_symptom_log():
    """Create or update a symptom log"""
    try:
        user_id = get_jwt_identity()
        
        # Get data from request
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Validate required fields
        required_fields = ['symptom_id', 'date', 'severity']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Add user_id to the symptom log data
        data['user_id'] = user_id
        
        # Create symptom log
        created_log = SymptomLog.create(data)
        
        return jsonify({
            "message": "Symptom log saved successfully",
            "log_id": str(created_log._id),
            "log": created_log.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating symptom log: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/', methods=['GET'])
@jwt_required()
def get_symptom_logs():
    """Get all symptom logs with optional filters"""
    try:
        user_id = get_jwt_identity()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        date = request.args.get('date')
        
        # Apply filters if provided
        if start_date and end_date:
            logs = SymptomLog.find_by_date_range(user_id, start_date, end_date)
        elif date:
            logs = SymptomLog.find_by_date(user_id, date)
        else:
            # Default to last 7 days if no filters
            today = datetime.now().strftime("%Y-%m-%d")
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            logs = SymptomLog.find_by_date_range(user_id, week_ago, today)
        
        return jsonify([log.to_dict() for log in logs]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error retrieving symptom logs: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_symptom_logs():
    """Get symptom logs for today"""
    try:
        user_id = get_jwt_identity()
        today = datetime.now().strftime("%Y-%m-%d")
        
        logs = SymptomLog.find_by_date(user_id, today)
        return jsonify([log.to_dict() for log in logs]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error retrieving today's symptom logs: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/date/<date>', methods=['GET'])
@jwt_required()
def get_logs_for_date(date):
    """Get all symptom logs for a specific date"""
    try:
        user_id = get_jwt_identity()
        
        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Get logs
        logs = SymptomLog.find_by_date(user_id, date)
        
        # Get symptom details
        symptoms = SymptomLog.get_symptom_details()
        
        # Enrich logs with symptom details
        enriched_logs = []
        for log in logs:
            log_dict = log.to_dict()
            symptom_id = log_dict['symptom_id']
            if symptom_id in symptoms:
                symptom_info = symptoms[symptom_id]
                enriched_logs.append({
                    "log_id": log_dict['_id'],
                    "symptom_id": symptom_id,
                    "symptom_name": symptom_info['name'],
                    "symptom_icon": symptom_info['icon'],
                    "category_name": symptom_info['categoryName'],
                    "category_icon": symptom_info['categoryIcon'],
                    "severity": log_dict['severity'],
                    "notes": log_dict['notes'],
                    "date": log_dict['date']
                })
        
        return jsonify({"logs": enriched_logs}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting logs for date: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/active/<date>', methods=['GET'])
@jwt_required()
def get_active_logs_for_date(date):
    """Get active symptom logs for a specific date (severity not 'none')"""
    try:
        user_id = get_jwt_identity()
        
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Get active logs
        logs = SymptomLog.find_active_symptoms_for_date(user_id, date)
        
        # Get symptom details
        symptoms = SymptomLog.get_symptom_details()
        
        # Enrich logs with symptom details
        enriched_logs = []
        for log in logs:
            log_dict = log.to_dict()
            symptom_id = log_dict['symptom_id']
            if symptom_id in symptoms:
                symptom_info = symptoms[symptom_id]
                enriched_logs.append({
                    "log_id": log_dict['_id'],
                    "symptom_id": symptom_id,
                    "symptom_name": symptom_info['name'],
                    "symptom_icon": symptom_info['icon'],
                    "category_name": symptom_info['categoryName'],
                    "category_icon": symptom_info['categoryIcon'],
                    "severity": log_dict['severity'],
                    "notes": log_dict['notes'],
                    "date": log_dict['date']
                })
        
        return jsonify({"logs": enriched_logs}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting active logs for date: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/range', methods=['GET'])
@jwt_required()
def get_logs_for_date_range():
    """Get symptom logs for a date range"""
    try:
        user_id = get_jwt_identity()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validate required parameters
        if not start_date or not end_date:
            return jsonify({"error": "Both start_date and end_date are required"}), 400
        
        # Validate date format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Get logs
        logs = SymptomLog.find_by_date_range(user_id, start_date, end_date)
        
        return jsonify({"logs": [log.to_dict() for log in logs]}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting logs for date range: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/dates-with-symptoms', methods=['GET'])
@jwt_required()
def get_dates_with_symptoms():
    """Get all dates where the user has logged symptoms"""
    try:
        user_id = get_jwt_identity()
        
        dates = SymptomLog.get_dates_with_symptoms(user_id)
        return jsonify({"dates": dates}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting dates with symptoms: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/<log_id>', methods=['DELETE'])
@jwt_required()
def delete_symptom_log(log_id):
    """Delete a symptom log"""
    try:
        user_id = get_jwt_identity()
        
        # Delete log
        deleted = SymptomLog.delete_log(user_id, log_id)
        if not deleted:
            return jsonify({"error": "Symptom log not found"}), 404
        
        return jsonify({"message": "Symptom log deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error deleting symptom log: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/summary/<date>', methods=['GET'])
@jwt_required()
def get_symptoms_summary(date):
    """Get a summary of symptoms by category for a specific date"""
    try:
        user_id = get_jwt_identity()
        
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Get active logs
        logs = SymptomLog.find_active_symptoms_for_date(user_id, date)
        
        # Get symptom details
        symptoms = SymptomLog.get_symptom_details()
        
        # Group by category
        categories = {
            "general": {"name": "General", "icon": "🔍", "symptoms": []},
            "mood": {"name": "Mood", "icon": "😊", "symptoms": []},
            "sleep": {"name": "Sleep", "icon": "😴", "symptoms": []},
            "digestive": {"name": "Digestive", "icon": "🍽️", "symptoms": []},
            "appetite": {"name": "Appetite", "icon": "🥑", "symptoms": []},
            "activity": {"name": "Physical Activity", "icon": "🏃‍♀️", "symptoms": []}
        }
        
        # Parse notes from any log
        notes = ""
        for log in logs:
            log_dict = log.to_dict()
            if log_dict.get('notes'):
                notes = log_dict['notes']
                break
        
        # Populate categories with symptoms
        for log in logs:
            log_dict = log.to_dict()
            symptom_id = log_dict['symptom_id']
            if symptom_id in symptoms:
                symptom_info = symptoms[symptom_id]
                category_name = symptom_info['categoryName'].lower()
                
                # Map category name to id if needed
                category_id = ""
                if "general" in category_name:
                    category_id = "general"
                elif "mood" in category_name:
                    category_id = "mood"
                elif "sleep" in category_name:
                    category_id = "sleep"
                elif "digestive" in category_name:
                    category_id = "digestive"
                elif "appetite" in category_name:
                    category_id = "appetite"
                elif "activity" in category_name or "physical" in category_name:
                    category_id = "activity"
                
                if category_id in categories:
                    categories[category_id]["symptoms"].append({
                        "id": symptom_id,
                        "name": symptom_info['name'],
                        "icon": symptom_info['icon'],
                        "severity": log_dict['severity']
                    })
        
        # Filter out empty categories
        summary = {
            "categories": [cat for cat in categories.values() if cat["symptoms"]],
            "notes": notes,
            "date": date
        }
        
        return jsonify(summary), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting symptoms summary: {str(e)}")
        return jsonify({"error": str(e)}), 500