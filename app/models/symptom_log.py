from app.db.db import get_database as get_db
from datetime import datetime, UTC
from bson.objectid import ObjectId


class SymptomLog:
    def __init__(self, log_data: dict):
        self.mongo_id = str(log_data.get('_id'))  # ⬅️ Add this line
        self.symptom_log_id = log_data.get('symptomLogId')
        self.user_id = log_data.get('userId')
        self.symptom = log_data.get('symptom')
        self.rating = log_data.get('rating')
        self.log_date = log_data.get('logDate')
        self.comments = log_data.get('comments')
        self.intake_log_id = log_data.get('intakeLogId')
        self.created_at = log_data.get('createdAt')
        self.updated_at = log_data.get('updatedAt')

    def to_dict(self):
        return {
            "_id": self.mongo_id,
            "symptomLogId": self.symptom_log_id,
            "userId": self.user_id,
            "symptom": self.symptom,
            "rating": self.rating,
            "logDate": self.log_date,
            "comments": self.comments,
            "intakeLogId": self.intake_log_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }


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
    def find_by_user(user_id: str, start_date: str = None, end_date: str = None):
        db = get_db()
        query = {'userId': user_id}
        
        if start_date and end_date:
            query['logDate'] = {'$gte': start_date, '$lte': end_date}
        elif start_date:
            query['logDate'] = {'$gte': start_date}
        elif end_date:
            query['logDate'] = {'$lte': end_date}
        
        query = {'userId': user_id, 'deleted': {'$ne': True}}

        return [SymptomLog(log) for log in db.SymptomLogs.find(query)]

    @staticmethod
    def update(mongo_id, updated_data: dict):
        db = get_db()
        result = db.SymptomLogs.update_one(
            {"_id": mongo_id},
            {"$set": updated_data}
        )
        return result.modified_count > 0

    @staticmethod
    def find_by_id(mongo_id):
        db = get_db()
        data = db.SymptomLogs.find_one({"_id": mongo_id, "deleted": {"$ne": True}})
        return SymptomLog(data) if data else None


    @staticmethod
    def delete(mongo_id, soft_delete=True):
        db = get_db()
        if soft_delete:
            result = db.SymptomLogs.update_one(
                {"_id": mongo_id},
                {"$set": {"deleted": True, "updatedAt": datetime.now(UTC).isoformat()}}
            )
        else:
            result = db.SymptomLogs.delete_one({"_id": mongo_id})
        return result.modified_count > 0 or result.deleted_count > 0