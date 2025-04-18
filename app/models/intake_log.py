from app.db.db import get_database as get_db
from datetime import datetime, timezone, timedelta
from bson.objectid import ObjectId
import uuid


class IntakeLog:
    def __init__(self, log_data: dict):
        self._id = log_data.get('_id')
        self.intake_log_id = log_data.get('intakeLogId')
        self.user_id = log_data.get('userId')
        self.supplement_id = log_data.get('supplementId')
        self.supplement_name = log_data.get('supplementName')
        self.timestamp = log_data.get('timestamp')  # ISO format datetime
        self.dosage = log_data.get('dosage')
        self.timing = log_data.get('timing')  # Morning, Afternoon, Evening, etc.
        #self.with_food = log_data.get('withFood', False)
        self.notes = log_data.get('notes')
        self.created_at = log_data.get('createdAt')
        self.updated_at = log_data.get('updatedAt')
        self.deleted_at = log_data.get('deletedAt')
       
    def to_dict(self):
        """Convert intake log to dictionary"""
        result = {
            "_id": str(self._id) if self._id else None,
            "intakeLogId": self.intake_log_id,
            "userId": self.user_id,
            "supplementId": self.supplement_id,
            "supplementName": self.supplement_name,
            "timestamp": self.timestamp,
            "dosage": self.dosage,
            "timing": self.timing,
            #"withFood": self.with_food,
            "notes": self.notes,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
       
        # Include optional fields if they exist
        if self._id:
            result["_id"] = str(self._id)
           
        if self.intake_log_id:
            result["intakeLogId"] = self.intake_log_id
           
        return result


    @staticmethod
    def create(log_data: dict):
        """Create a new intake log"""
        db = get_db()
       
        # Validate required fields
        required_fields = ['userId', 'supplementId']
        for field in required_fields:
            if field not in log_data or not log_data[field]:
                raise ValueError(f"Missing required field: {field}")
               
        # Add timestamps
        now = datetime.now().isoformat()
        if 'timestamp' not in log_data:
            log_data['timestamp'] = now
           
        log_data['createdAt'] = now
        log_data['updatedAt'] = now
       
        # Try to get supplement name if not provided
        if 'supplementName' not in log_data or not log_data['supplementName']:
            try:
                supplement = db.Supplements.find_one({
                    '$or': [
                        {'_id': ObjectId(log_data['supplementId'])},
                        {'supplementId': log_data['supplementId']}
                    ],
                    'deletedAt': None
                })
               
                if supplement and 'name' in supplement:
                    log_data['supplementName'] = supplement['name']
            except Exception:
                # If we can't find the supplement name, continue without it
                pass

        # Generate unique intakeLogId if not provided
        if 'intakeLogId' not in log_data or not log_data['intakeLogId']:
            unique_suffix = uuid.uuid4().int % (10 ** 12)
            log_data['intakeLogId'] = f"INTAKE{unique_suffix}"
                    
        # Insert into database
        result = db.IntakeLogs.insert_one(log_data)
       
        if not result.inserted_id:
            raise ValueError("Failed to create intake log")
           
        # Return the created log
        created_data = log_data.copy()
        created_data['_id'] = result.inserted_id
        return IntakeLog(created_data)


    @staticmethod
    def find_by_id(_id):
        """Find an intake log by ID"""
        db = get_db()
        try:
            # Convert string ID to ObjectId if necessary
            if isinstance(_id, str):
                _id = ObjectId(_id)
               
            # Find log
            log = db.IntakeLogs.find_one({'_id': _id, 'deletedAt': None})
            return IntakeLog(log) if log else None
        except Exception as e:
            raise ValueError(f"Error finding intake log: {e}")
   
    @staticmethod
    def find_all(query=None):
        """Find all intake logs matching a query"""
        db = get_db()
        try:
            # Default query filters out deleted logs
            if query is None:
                query = {}
            query['deletedAt'] = None
           
            # Find logs
            logs = list(db.IntakeLogs.find(query))
            return [IntakeLog(log) for log in logs]
        except Exception as e:
            raise ValueError(f"Error finding intake logs: {e}")
   
    @staticmethod
    def find_by_user(user_id, start_date=None, end_date=None):
        """Find logs for a specific user with optional date filtering"""
        db = get_db()
        query = {'userId': user_id, 'deletedAt': None}
       
        if start_date and end_date:
            query['timestamp'] = {'$gte': start_date, '$lte': end_date}
           
        return [IntakeLog(log) for log in db.IntakeLogs.find(query)]
   
    @staticmethod
    def find_by_date_range(user_id, start_date, end_date):
        """Find logs within a specific date range"""
        db = get_db()
        query = {
            'userId': user_id,
            'timestamp': {'$gte': start_date, '$lte': end_date},
            'deletedAt': None
        }
       
        return [IntakeLog(log) for log in db.IntakeLogs.find(query)]
   
    @staticmethod
    def find_recent(user_id, hours=24):
        """Find logs from the past X hours"""
        db = get_db()
        # Calculate the timestamp for X hours ago
        now = datetime.now()
        past_time = (now - timedelta(hours=hours)).isoformat()
       
        query = {
            'userId': user_id,
            'timestamp': {'$gte': past_time},
            'deletedAt': None
        }
       
        return [IntakeLog(log) for log in db.IntakeLogs.find(query)]
   
    @staticmethod
    def update(_id, update_data):
        """Update an intake log"""
        db = get_db()
        try:
            # Convert string ID to ObjectId if necessary
            if isinstance(_id, str):
                _id = ObjectId(_id)
               
            # Check if log exists
            existing = db.IntakeLogs.find_one({'_id': _id, 'deletedAt': None})
            if not existing:
                raise ValueError(f"Intake log not found with ID: {_id}")
               
            # Update timestamp
            update_data['updatedAt'] = datetime.now().isoformat()
           
            # Update in database
            db.IntakeLogs.update_one({'_id': _id}, {'$set': update_data})
           
            # Return updated log
            updated = db.IntakeLogs.find_one({'_id': _id})
            return IntakeLog(updated)
        except Exception as e:
            raise ValueError(f"Error updating intake log: {e}")
   
    @staticmethod
    def delete(_id, soft_delete=True):
        """Delete an intake log"""
        db = get_db()
        try:
            # Convert string ID to ObjectId if necessary
            if isinstance(_id, str):
                _id = ObjectId(_id)
               
            # Check if log exists
            existing = db.IntakeLogs.find_one({'_id': _id, 'deletedAt': None})
            if not existing:
                return None
               
            if soft_delete:
                # Soft delete
                db.IntakeLogs.update_one(
                    {'_id': _id},
                    {'$set': {'deletedAt': datetime.now().isoformat()}}
                )
                updated = db.IntakeLogs.find_one({'_id': _id})
                return IntakeLog(updated)
            else:
                # Hard delete
                db.IntakeLogs.delete_one({'_id': _id})
                return IntakeLog(existing)
        except Exception as e:
            raise ValueError(f"Error deleting intake log: {e}")

