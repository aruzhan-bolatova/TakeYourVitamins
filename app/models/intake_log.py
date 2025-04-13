from app.db.db import get_database as get_db
from datetime import datetime, UTC

class IntakeLog:
    def __init__(self, log_data: dict):
        self.intake_log_id = log_data.get('intakeLogId')
        self.user_id = log_data.get('userId')
        self.supplement_id = log_data.get('supplementId')
        self.intake_date = log_data.get('intakeDate')
        self.intake_time = log_data.get('intakeTime')
        self.dosage = log_data.get('dosage')
        self.notes = log_data.get('notes')
        self.created_at = log_data.get('createdAt')
        self.updated_at = log_data.get('updatedAt')
        self.is_deleted = log_data.get('isDeleted')

    @staticmethod
    def create(user_id: str, supplement_id: str, intake_date: str, intake_time: str, dosage: str, notes: str = None):
        db = get_db()
        if not db.Supplements.find_one({'supplementId': supplement_id}):
            raise ValueError('Supplement not found')
        intake_log = {
            'intakeLogId': f"INTAKE{str(datetime.now(UTC).timestamp()).replace('.', '')}",
            'userId': user_id,
            'supplementId': supplement_id,
            'intakeDate': intake_date,
            'intakeTime': intake_time,
            'dosage': dosage,
            'notes': notes,
            'createdAt': datetime.now(UTC).isoformat(),
            'updatedAt': None,
            'isDeleted': False
        }
        db.IntakeLogs.insert_one(intake_log)
        return IntakeLog(intake_log)

    @staticmethod
    def find_by_user(user_id: str, start_date: str = None, end_date: str = None):
        db = get_db()
        query = {'userId': user_id, 'isDeleted': False}
        if start_date and end_date:
            query['intakeDate'] = {'$gte': start_date, '$lte': end_date}
        return [IntakeLog(log) for log in db.IntakeLogs.find(query)]