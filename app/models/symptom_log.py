from app.db.db import get_database as get_db
from datetime import datetime, timezone
from bson.objectid import ObjectId

class SymptomLog:
    def __init__(self, log_data: dict):
        self.symptom_log_id = log_data.get('symptomLogId')
        self.user_id = log_data.get('userId')
        self.symptom = log_data.get('symptom')
        self.rating = log_data.get('rating')
        self.log_date = log_data.get('logDate')
        self.comments = log_data.get('comments')
        self.intake_log_id = log_data.get('intakeLogId')
        self.created_at = log_data.get('createdAt')
        self.updated_at = log_data.get('updatedAt')
        self.is_deleted = log_data.get('isDeleted')

    def to_dict(self):
        """Convert the symptom log to a dictionary"""
        return {
            'symptomLogId': self.symptom_log_id,
            'userId': self.user_id,
            'symptom': self.symptom,
            'rating': self.rating,
            'logDate': self.log_date,
            'comments': self.comments,
            'intakeLogId': self.intake_log_id,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
            'isDeleted': self.is_deleted
        }

    def validate_data(self, data):
        """Validate the symptom log data"""
        required_fields = ['userId', 'symptom', 'rating', 'logDate']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate rating is within acceptable range (1-10)
        if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 10:
            raise ValueError("Rating must be an integer between 1 and 10")
        
        # Validate date format
        try:
            datetime.fromisoformat(data['logDate'])
        except ValueError:
            raise ValueError("Invalid date format for logDate. Expected ISO format.")
        
        return True

    @staticmethod
    def create(user_id: str, symptom: str, rating: int, log_date: str, comments: str = None, intake_log_id: str = None):
        db = get_db()
        symptom_log = {
            'symptomLogId': f"SYMPTOM{str(datetime.now(timezone.utc).timestamp()).replace('.', '')}",
            'userId': user_id,
            'symptom': symptom,
            'rating': rating,
            'logDate': log_date,
            'comments': comments,
            'intakeLogId': intake_log_id,
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'updatedAt': None,
            'isDeleted': False
        }
        db.SymptomLogs.insert_one(symptom_log)
        return SymptomLog(symptom_log)

    @staticmethod
    def find_by_id(log_id):
        """Find a symptom log by ID"""
        db = get_db()
        log = db.SymptomLogs.find_one({'_id': log_id, 'isDeleted': False})
        if log:
            return SymptomLog(log)
        return None

    @staticmethod
    def find_by_user(user_id: str, start_date: str = None):
        db = get_db()
        query = {'userId': user_id, 'isDeleted': False}
        if start_date:
            query['logDate'] = {'$gte': start_date}
        return [SymptomLog(log) for log in db.SymptomLogs.find(query)]

    @staticmethod
    def search(user_id: str = None, date_from: str = None, date_to: str = None):
        """Search for symptom logs with optional filters"""
        db = get_db()
        query = {'isDeleted': False}
        
        if user_id:
            query['userId'] = user_id
        
        if date_from or date_to:
            query['logDate'] = {}
            if date_from:
                query['logDate']['$gte'] = date_from
            if date_to:
                query['logDate']['$lte'] = date_to
                
        return [SymptomLog(log) for log in db.SymptomLogs.find(query)]

    @staticmethod
    def update(log_id, update_data):
        """Update a symptom log"""
        db = get_db()
        
        # Find existing log
        existing_log = db.SymptomLogs.find_one({'_id': log_id, 'isDeleted': False})
        if not existing_log:
            raise ValueError("Symptom log not found")
        
        # Create a new log instance with existing data for validation
        log = SymptomLog(existing_log)
        
        # Filter out non-updatable fields
        updatable = {k: v for k, v in update_data.items() 
                    if k not in ['symptomLogId', 'createdAt', 'isDeleted']}
        
        # Validate updated data
        combined_data = {**existing_log, **updatable}
        log.validate_data(combined_data)
        
        # Add updated timestamp
        updatable['updatedAt'] = datetime.now(timezone.utc).isoformat()
        
        # Update the document
        result = db.SymptomLogs.update_one(
            {'_id': log_id, 'isDeleted': False},
            {'$set': updatable}
        )
        
        return result.modified_count > 0

    @staticmethod
    def delete(log_id, soft_delete=True):
        """Delete a symptom log"""
        db = get_db()
        
        if soft_delete:
            result = db.SymptomLogs.update_one(
                {'_id': log_id, 'isDeleted': False},
                {'$set': {
                    'isDeleted': True,
                    'updatedAt': datetime.now(timezone.utc).isoformat()
                }}
            )
            return result.modified_count > 0
        else:
            result = db.SymptomLogs.delete_one({'_id': log_id})
            return result.deleted_count > 0