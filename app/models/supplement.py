from app.db.db import get_database as get_db
from datetime import datetime

class Supplement:
    REQUIRED_FIELDS = ['supplementId', 'name', 'description']
    def __init__(self, supplement_data: dict):
        self._id = supplement_data.get('_id')
        self.supplement_id = supplement_data.get('supplementId')
        self.name = supplement_data.get('name')
        self.aliases = supplement_data.get('aliases', [])
        self.description = supplement_data.get('description')
        self.intake_practices = supplement_data.get('intakePractices', {})
        self.scientific_details = supplement_data.get('scientificDetails', {})
        self.category = supplement_data.get('category')
        self.updated_at = supplement_data.get('updatedAt')

    def validate_data(self, supplement_data):
        for field in self.REQUIRED_FIELDS:
            if field not in supplement_data or not supplement_data[field]:
                raise ValueError(f"Missing required field: {field}")
            
    def to_dict(self):
        # Create base dictionary
        result = {
            "supplementId": self.supplement_id,
            "name": self.name,
            "aliases": self.aliases,
            "description": self.description,
            "intakePractices": self.intake_practices,
            "scientificDetails": self.scientific_details,
            "category": self.category,
            "updatedAt": self.updated_at
        }
        
        # Only include _id if it exists
        if self._id:
            result["_id"] = str(self._id)
            
        return result

    @staticmethod
    def search(search_query: str, field: str = 'name'):
        db = get_db()
        query = {field: {'$regex': search_query, '$options': 'i'}} if search_query else {}
        return [Supplement(s) for s in db.Supplements.find(query)]

    @staticmethod
    def find_by_id(_id: str):
        db = get_db()
        try:
            supplement = db.Supplements.find_one({'_id': _id})
            return Supplement(supplement) if supplement else None
        except Exception as e:
            raise ValueError(f"Error finding supplement by ID: {e}")
    
    # Method to update an existing supplement
    @staticmethod
    def update(_id: str, supplement_data: dict):
        db = get_db()
        try:
            # Fetch the existing supplement
            existing_supplement = db.Supplements.find_one({'_id': _id})
            if not existing_supplement:
                raise ValueError(f"Supplement with ID {_id} not found.")
            
            # Merge the existing data with the new data
            updated_data = {**existing_supplement, **supplement_data}
            
            # Validate the merged data
            supplement = Supplement(updated_data)
            supplement.validate_data(updated_data)
            
            # Update the supplement in the database
            db.Supplements.update_one(
                {'_id': _id},
                {'$set': supplement_data}
            )
        except Exception as e:
            raise ValueError(f"Error updating supplement: {e}")
        
    # Method to delete a supplement
    @staticmethod
    def delete(_id: str, soft_delete: bool = True):
        db = get_db()
        if soft_delete:
            # Perform a soft delete by setting a deletedAt timestamp
            result = db.Supplements.update_one(
                {'_id': _id},
                {'$set': {'deletedAt': datetime.now().isoformat()}}
            )
        else:
            # Perform a hard delete by removing the document
            result = db.Supplements.delete_one({'_id': _id})
        return result.deleted_count > 0 if not soft_delete else result.modified_count > 0