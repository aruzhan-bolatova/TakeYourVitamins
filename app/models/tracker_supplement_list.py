from app.db.db import get_database as get_db
from bson.objectid import ObjectId
from datetime import datetime

class TrackedSupplement:
    REQUIRED_FIELDS = ['supplement_id','dosage','frequency','duration']

    def __init__(self, tracked_supplement_data: dict):
        self.supplement_id = tracked_supplement_data.get('supplementId')
        self.supplement_name = tracked_supplement_data.get('supplementName')
        self.dosage = tracked_supplement_data.get('dosage')
        self.unit = tracked_supplement_data.get('unit')
        self.frequency = tracked_supplement_data.get('frequency')
        self.duration = tracked_supplement_data.get('duration')
        self.start_date = tracked_supplement_data.get('startDate')
        self.end_date = tracked_supplement_data.get('endDate')
        self.notes = tracked_supplement_data.get('notes')
        self.created_at = tracked_supplement_data.get('createdAt')
        self.updated_at = tracked_supplement_data.get('updatedAt')

    def to_dict(self):
        """Convert tracked supplement to dictionary"""
        return {
            "supplementId": self.supplement_id,
            "supplementName": self.supplement_name,
            "dosage": self.dosage,
            "unit": self.unit,
            "frequency": self.frequency,
            "duration": self.duration,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "notes": self.notes,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }

    def validate_data(self):
        """Validate the tracked supplement data"""
        for field in self.REQUIRED_FIELDS:
            if field not in self.__dict__ or not self.__dict__[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Additional validation can be added here as needed

    @staticmethod
    def create(tracked_supplement_data: dict):
        """Create a new interaction"""
        # Validate data
        tracked_supplement_info = TrackedSupplement(tracked_supplement_data)
        tracked_supplement_info.validate_data()
        
        # Add timestamps
        now = datetime.now().isoformat()
        tracked_supplement_info['createdAt'] = now
        tracked_supplement_info['updatedAt'] = now
        
        return tracked_supplement_info





class TrackerSupplementList:
    REQUIRED_FIELDS = ['user_id']
    
    def __init__(self, userId: str):
        # self.user_id = intake_list_data.get('user_id')
        # self.supplements = [TrackedSupplement(supp) for supp in intake_list_data.get('supplements', [])]
        self.user_id = userId
        self.tracked_supplements = []

    def get_supplement_names(self):
        """
        Returns a list of supplement names from the supplements array.
        Handles cases where the name is null or missing.
        """
        return [supplement.supplement_name for supplement in self.tracked_supplements if supplement.supplement_name]

    #TODO: Add a method to get the supplement list by userId

    @staticmethod
    def create(userId: str):
        # Validate data
        tracker_supplement_list = TrackerSupplementList(userId)
        
        # Add timestamps
        now = datetime.now().isoformat()
        tracker_supplement_list_data = {
            "user_id": userId,
            "createdAt": now,
            "updatedAt": now,
            "tracked_supplements": []
        }
        
        # Insert into database
        db = get_db()
        result = db.Tracker_Supplement_List.insert_one(tracker_supplement_list_data)
        
        if not result.inserted_id:
            raise ValueError("Failed to create tracker supplement list")
            
        # Return the created tracker supplement list
        created_data = tracker_supplement_list_data.copy()
        created_data['_id'] = result.inserted_id
        return TrackerSupplementList(userId)
    
    @staticmethod
    def find_by_user_id(user_id):
        """Find tracker supplement list by user ID"""
        db = get_db()
        try:
            # Find tracker supplement list
            tracker_supplement_list = db.Tracker_Supplement_List.find_one({'user_id': user_id, 'deletedAt': None})
            return TrackerSupplementList(user_id) if tracker_supplement_list else None
        except Exception as e:
            raise ValueError(f"Error finding tracker supplement list: {e}")
    
    @staticmethod
    def add_tracked_supplement(user_id, tracked_supplement_data):
        """Add a tracked supplement to the list"""
        db = get_db()
        try:
            # Validate data
            tracked_supplement = TrackedSupplement.create(tracked_supplement_data)
            
            # Add to database
            db.Tracker_Supplement_List.update_one(
                {'user_id': user_id},
                {'$push': {'tracked_supplements': tracked_supplement.to_dict()}}
            )
            
            # Return updated tracker supplement list
            updated_list = db.Tracker_Supplement_List.find_one({'user_id': user_id})
            return TrackerSupplementList(user_id) if updated_list else None
        except Exception as e:
            raise ValueError(f"Error adding tracked supplement: {e}")
    
    @staticmethod
    def delete_tracked_supplement(user_id, supplement_id):
        """Delete a tracked supplement from the list"""
        db = get_db()
        try:
            # Remove from database
            db.Tracker_Supplement_List.update_one(
                {'user_id': user_id},
                {'$pull': {'tracked_supplements': {'_id': ObjectId(supplement_id)}}}
            )
            
            # Return updated tracker supplement list
            updated_list = db.Tracker_Supplement_List.find_one({'user_id': user_id})
            return TrackerSupplementList(user_id) if updated_list else None
        except Exception as e:
            raise ValueError(f"Error deleting tracked supplement: {e}")
    
    @staticmethod
    def update_tracked_supplement(user_id, supplement_id, updated_data):
        """Update a tracked supplement in the list"""
        db = get_db()
        try:
            # Update in database
            db.Tracker_Supplement_List.update_one(
                {'user_id': user_id, 'tracked_supplements._id': ObjectId(supplement_id)},
                {'$set': {'tracked_supplements.$': updated_data}}
            )
            
            # Return updated tracker supplement list
            updated_list = db.Tracker_Supplement_List.find_one({'user_id': user_id})
            return TrackerSupplementList(user_id) if updated_list else None
        except Exception as e:
            raise ValueError(f"Error updating tracked supplement: {e}")

    #possible TODO: delete the entire tracker supplement list for a user
    
    