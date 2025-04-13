from app.db.db import get_database as get_db
from datetime import datetime, UTC

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

    @staticmethod
    def create(user_id: str, symptom: str, rating: int, log_date: str, comments: str = None, intake_log_id: str = None):
        db = get_db()
        symptom_log = {
            'symptomLogId': f"SYMPTOM{str(datetime.now(UTC).timestamp()).replace('.', '')}",
            'userId': user_id,
            'symptom': symptom,
            'rating': rating,
            'logDate': log_date,
            'comments': comments,
            'intakeLogId': intake_log_id,
            'createdAt': datetime.now(UTC).isoformat(),
            'updatedAt': None
        }
        db.SymptomLogs.insert_one(symptom_log)
        return SymptomLog(symptom_log)

    @staticmethod
    def find_by_user(user_id: str, start_date: str = None):
        db = get_db()
        query = {'userId': user_id}
        if start_date:
            query['logDate'] = {'$gte': start_date}
        return [SymptomLog(log) for log in db.SymptomLogs.find(query)]