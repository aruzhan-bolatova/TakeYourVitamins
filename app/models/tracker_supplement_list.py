from app.db.db import get_database as get_db
from bson.objectid import ObjectId
from datetime import datetime

class TrackedSupplement:
    REQUIRED_FIELDS = ['supplement_id','dosage','frequency','duration']

    def __init__(self, tracked_supplement_data: dict):
        self._id = tracked_supplement_data.get('_id')
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
        self.deleted_at = tracked_supplement_data.get('deletedAt')

    def to_dict(self):
        """Convert tracked supplement to dictionary"""
        return {
            "_id": str(self._id) if self._id else None,
            "supplementId": str(self.supplement_id) ,
            "supplementName": self.supplement_name,
            "dosage": self.dosage,
            "unit": self.unit,
            "frequency": self.frequency,
            "duration": self.duration,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "notes": self.notes,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "deletedAt": self.deleted_at
            
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
        if not tracked_supplement_data:
            raise ValueError("Tracked supplement data is required")
        
        # Set default values for optional fields
        tracked_supplement_data['unit'] = tracked_supplement_data.get('unit', 'mg')
        tracked_supplement_data['start_date'] = tracked_supplement_data.get('startDate', datetime.now().isoformat())
        tracked_supplement_data['end_date'] = tracked_supplement_data.get('endDate', None)
        tracked_supplement_data['notes'] = tracked_supplement_data.get('notes', '')
        tracked_supplement_data['duration'] = tracked_supplement_data.get('duration', 0)
        tracked_supplement_data.validate_data()
        
        tracked_supplement_data['_id'] = ObjectId() # Generate a new ObjectId for the supplement
        
        # Add timestamps
        now = datetime.now().isoformat()
        tracked_supplement_data['createdAt'] = now
        tracked_supplement_data['updatedAt'] = now
        tracked_supplement_data['deletedAt'] = None
        
        tracked_supplement_info = TrackedSupplement(tracked_supplement_data)
        return tracked_supplement_info


class TrackerSupplementList:
    REQUIRED_FIELDS = ['user_id']
    
    def __init__(self, data: dict):
        self._id = data.get('_id', ObjectId())  # Generate a new ObjectId if not provided
        self.user_id = data.get('user_id')  # Associate with the user's _id
        self.tracked_supplements = [
            TrackedSupplement(supplement) for supplement in data.get('tracked_supplements', [])
        ]
        self.created_at = data.get('createdAt', datetime.now().isoformat())
        self.updated_at = data.get('updatedAt', datetime.now().isoformat())
        self.deleted_at = data.get('deletedAt', None)
        

    def get_supplement_names(self):
        """
        Returns a list of supplement names from the supplements array.
        Handles cases where the name is null or missing.
        """
        return [supplement.supplement_name for supplement in self.tracked_supplements if supplement.supplement_name]

    def to_dict(self):
        """Convert the TrackerSupplementList object to a dictionary."""
        return {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'tracked_supplements': [supplement.to_dict() for supplement in self.tracked_supplements],
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
            'deletedAt': self.deleted_at
        }
    @staticmethod
    def create_for_user(user_id: str):
        print(f"Creating TrackerSupplementList for user: {user_id}")
        """Create a new TrackerSupplementList for a user."""
        db = get_db()

        # Check if a list already exists for the user
        existing_list = db.TrackerSupplementList.find_one({'user_id': ObjectId(user_id)})
        if existing_list:
            raise ValueError("TrackerSupplementList already exists for this user")

        # Create a new list
        now = datetime.now().isoformat()
        tracker_supplement_list_data = {
            'user_id': ObjectId(user_id),
            'tracked_supplements': [],
            'createdAt': now,
            'updatedAt': now,
        }
        result = db.TrackerSupplementList.insert_one(tracker_supplement_list_data)
        tracker_supplement_list_data['_id'] = result.inserted_id
        return TrackerSupplementList(tracker_supplement_list_data)

    @staticmethod
    def find_by_user_id(user_id: str):
        print(f"Finding TrackerSupplementList for user: {user_id}")
        """Find a TrackerSupplementList by user ID."""
        db = get_db()
        tracker_supplement_list = db.TrackerSupplementList.find_one({'user_id': ObjectId(user_id)})
        return TrackerSupplementList(tracker_supplement_list) if tracker_supplement_list else None

    @staticmethod
    def add_tracked_supplement(user_id: str, tracked_supplement_data: dict):
        """Add a TrackedSupplement to the user's TrackerSupplementList."""
        db = get_db()

        # Find the user's list
        tracker_supplement_list = db.TrackerSupplementList.find_one({'user_id': ObjectId(user_id)})
        if not tracker_supplement_list:
            raise ValueError("TrackerSupplementList not found for the user")

        tracked_supplement_data['_id'] = ObjectId()  # Generate a new ObjectId for the supplement
        tracked_supplement_data['supplementId'] = ObjectId(tracked_supplement_data.get('supplementId'))
        # Create a new TrackedSupplement
        print(f"Creating TrackedSupplement with data: {tracked_supplement_data}")
        tracked_supplement = TrackedSupplement(tracked_supplement_data)

        # Add the supplement to the list
        db.TrackerSupplementList.update_one(
            {'user_id': ObjectId(user_id)},
            {'$push': {'tracked_supplements': tracked_supplement.to_dict()}}
        )

        # Return the updated list
        updated_list = db.TrackerSupplementList.find_one({'user_id': ObjectId(user_id)})
        for supplement in updated_list['tracked_supplements']:
            supplement['_id'] = str(supplement['_id'])
            supplement['supplementId'] = str(supplement['supplementId'])
        return TrackerSupplementList(updated_list)

    @staticmethod
    def delete_tracked_supplement(user_id: str, supplement_id: str):
        """Delete a TrackedSupplement from the user's TrackerSupplementList."""
        db = get_db()

        # Remove the supplement from the list
        db.TrackerSupplementList.update_one(
            {'user_id': ObjectId(user_id)},
            {'$pull': {'tracked_supplements': {'_id': supplement_id}}}
        )

        # Return the updated list
        updated_list = db.TrackerSupplementList.find_one({'user_id': ObjectId(user_id)})
        return TrackerSupplementList(updated_list)
    
    @staticmethod
    def update_tracked_supplement(user_id: str, supplement_id: str, updated_data: dict):
        """Update a TrackedSupplement in the user's TrackerSupplementList."""
        db = get_db()

        # Update the supplement in the list
        db.TrackerSupplementList.update_one(
            {'user_id': ObjectId(user_id), 'tracked_supplements._id': ObjectId(supplement_id)},
            {'$set': {'tracked_supplements.$': updated_data}}
        )

        # Return the updated list
        updated_list = db.TrackerSupplementList.find_one({'user_id': ObjectId(user_id)})
        return TrackerSupplementList(updated_list)
