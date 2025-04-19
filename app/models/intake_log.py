from app.db.db import get_database as get_db
from bson.objectid import ObjectId
from datetime import datetime, timezone
import uuid

class IntakeLog:
    REQUIRED_FIELDS = ['user_id', 'tracked_supplement_id', 'intake_date']

    def __init__(self, intake_log_data: dict):
        self._id = intake_log_data.get('_id')
        self.user_id = intake_log_data.get('user_id')
        self.tracked_supplement_id = intake_log_data.get('tracked_supplement_id')
        self.supplement_name = intake_log_data.get('supplement_name')
        self.intake_date = intake_log_data.get('intake_date')
        self.intake_time = intake_log_data.get('intake_time')
        self.dosage_taken = intake_log_data.get('dosage_taken')
        self.unit = intake_log_data.get('unit')
        self.notes = intake_log_data.get('notes')
        self.created_at = intake_log_data.get('created_at')
        self.updated_at = intake_log_data.get('updated_at')
        self.deleted_at = intake_log_data.get('deleted_at')

    def to_dict(self):
        """Convert intake log to dictionary"""
        return {
            "_id": str(self._id) if self._id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "tracked_supplement_id": str(self.tracked_supplement_id) if self.tracked_supplement_id else None,
            "supplement_name": self.supplement_name,
            "intake_date": self.intake_date,
            "intake_time": self.intake_time,
            "dosage_taken": self.dosage_taken,
            "unit": self.unit,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at
        }

    def validate_data(self):
        """Validate the intake log data"""
        for field in self.REQUIRED_FIELDS:
            if not getattr(self, field):
                raise ValueError(f"Missing required field: {field}")

    @staticmethod
    def create(intake_log_data: dict):
        """Create a new intake log"""
        # Validate data
        if not intake_log_data:
            raise ValueError("Intake log data is required")

        db = get_db()
        
        # Prepare the intake log data
        now = datetime.now(timezone.utc).isoformat()
        
        # Default values
        intake_log_data['intake_time'] = intake_log_data.get('intake_time', now)
        intake_log_data['notes'] = intake_log_data.get('notes', '')
        # Assign a unique intakeLogId if it doesn't exist
        intake_log_data['intakeLogId'] = str(uuid.uuid4())
        
        # Convert string IDs to ObjectId
        if isinstance(intake_log_data.get('user_id'), str):
            intake_log_data['user_id'] = ObjectId(intake_log_data['user_id'])
            
        if isinstance(intake_log_data.get('tracked_supplement_id'), str):
            intake_log_data['tracked_supplement_id'] = ObjectId(intake_log_data['tracked_supplement_id'])
        
        # Get supplement name from tracked supplement if not provided
        if not intake_log_data.get('supplement_name'):
            # Find the tracked supplement to get its name
            tracker_list = db.TrackerSupplementList.find_one({'user_id': intake_log_data['user_id']})
            if tracker_list:
                for supplement in tracker_list.get('tracked_supplements', []):
                    if str(supplement.get('_id')) == str(intake_log_data['tracked_supplement_id']):
                        intake_log_data['supplement_name'] = supplement.get('supplementName')
                        intake_log_data['unit'] = supplement.get('unit')
                        break
        
        # Add timestamps
        intake_log_data['created_at'] = now
        intake_log_data['updated_at'] = now
        intake_log_data['deleted_at'] = None
        
        # Create object and validate
        intake_log = IntakeLog(intake_log_data)
        intake_log.validate_data()
        print("Creating intake log with data:", intake_log_data)
        
        # Insert into database
        result = db.IntakeLogs.insert_one(intake_log_data)
        
        if not result.inserted_id:
            raise ValueError("Failed to create intake log")
            
        # Get the created intake log with its ID
        created_log = db.IntakeLogs.find_one({"_id": result.inserted_id})
        return IntakeLog(created_log)

    @staticmethod
    def find_by_id(log_id: str):
        """Find an intake log by ID"""
        db = get_db()
        try:
            intake_log = db.IntakeLogs.find_one({'_id': ObjectId(log_id), 'deleted_at': None})
            return IntakeLog(intake_log) if intake_log else None
        except Exception as e:
            raise ValueError(f"Error finding intake log: {e}")

    @staticmethod
    def find_by_user_id(user_id: str):
        """Find all intake logs for a user"""
        db = get_db()
        try:
            intake_logs = db.IntakeLogs.find({'user_id': ObjectId(user_id), 'deleted_at': None})
            return [IntakeLog(log) for log in intake_logs]
        except Exception as e:
            raise ValueError(f"Error finding intake logs: {e}")

    @staticmethod
    def find_by_date_range(user_id: str, start_date: str, end_date: str):
        """Find intake logs within a date range for a user"""
        db = get_db()
        try:
            intake_logs = db.IntakeLogs.find({
                'user_id': ObjectId(user_id),
                'intake_date': {'$gte': start_date, '$lte': end_date},
                'deleted_at': None
            })
            return [IntakeLog(log) for log in intake_logs]
        except Exception as e:
            raise ValueError(f"Error finding intake logs by date range: {e}")

    @staticmethod
    def find_by_supplement_id(user_id: str, tracked_supplement_id: str):
        """Find intake logs for a specific supplement"""
        db = get_db()
        try:
            intake_logs = db.IntakeLogs.find({
                'user_id': ObjectId(user_id),
                'tracked_supplement_id': ObjectId(tracked_supplement_id),
                'deleted_at': None
            })
            return [IntakeLog(log) for log in intake_logs]
        except Exception as e:
            raise ValueError(f"Error finding intake logs by supplement: {e}")

    @staticmethod
    def update(log_id: str, update_data: dict):
        """Update an intake log"""
        db = get_db()
        try:
            # Find the log first
            existing_log = db.IntakeLogs.find_one({'_id': ObjectId(log_id), 'deleted_at': None})
            if not existing_log:
                raise ValueError("Intake log not found")
            
            # Update only allowed fields
            allowed_fields = ['intake_date', 'intake_time', 'dosage_taken', 'notes']
            update_dict = {k: v for k, v in update_data.items() if k in allowed_fields}
            
            if update_dict:
                update_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
                db.IntakeLogs.update_one(
                    {'_id': ObjectId(log_id)},
                    {'$set': update_dict}
                )
            
            # Return the updated log
            updated_log = db.IntakeLogs.find_one({'_id': ObjectId(log_id)})
            return IntakeLog(updated_log)
        except Exception as e:
            raise ValueError(f"Error updating intake log: {e}")

    @staticmethod
    def delete(log_id: str):
        """Soft delete an intake log"""
        db = get_db()
        try:
            # Find the log first
            existing_log = db.IntakeLogs.find_one({'_id': ObjectId(log_id), 'deleted_at': None})
            if not existing_log:
                raise ValueError("Intake log not found")
            
            # Soft delete by setting deleted_at
            now = datetime.now(timezone.utc).isoformat()
            db.IntakeLogs.update_one(
                {'_id': ObjectId(log_id)},
                {'$set': {
                    'deleted_at': now,
                    'updated_at': now
                }}
            )
            
            return True
        except Exception as e:
            raise ValueError(f"Error deleting intake log: {e}")

    @staticmethod
    def get_intake_summary(user_id: str, start_date: str = None, end_date: str = None):
        """Get a summary of supplement intake for a user over a time period"""
        db = get_db()
        try:
            match_query = {
                'user_id': ObjectId(user_id),
                'deleted_at': None
            }
            
            if start_date:
                match_query['intake_date'] = {'$gte': start_date}
                if end_date:
                    match_query['intake_date']['$lte'] = end_date
            
            pipeline = [
                {'$match': match_query},
                {'$group': {
                    '_id': '$tracked_supplement_id',
                    'supplement_name': {'$first': '$supplement_name'},
                    'total_intake': {'$sum': '$dosage_taken'},
                    'unit': {'$first': '$unit'},
                    'intake_count': {'$sum': 1},
                    'dates': {'$addToSet': '$intake_date'}
                }},
                {'$project': {
                    'supplement_id': '$_id',
                    '_id': 0,
                    'supplement_name': 1,
                    'total_intake': 1,
                    'unit': 1,
                    'intake_count': 1,
                    'days_taken': {'$size': '$dates'}
                }}
            ]
            
            summary = list(db.IntakeLogs.aggregate(pipeline))
            return summary
        except Exception as e:
            raise ValueError(f"Error generating intake summary: {e}")