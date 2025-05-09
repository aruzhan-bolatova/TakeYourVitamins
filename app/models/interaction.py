from app.db.db import get_database as get_db
from bson.objectid import ObjectId
from datetime import datetime

class Interaction:
    REQUIRED_FIELDS = ['supplements', 'interactionType', 'effect']
    VALID_INTERACTION_TYPES = ['Supplement-Supplement', 'Supplement-Food']
    VALID_EFFECTS = ['Enhances Absorption', 'Inhibits Absorption', 'No Effect']
    
    def __init__(self, interaction_data: dict):
        self._id = interaction_data.get('_id')
        self.interaction_id = interaction_data.get('interactionId')
        self.supplements = interaction_data.get('supplements', [])  # List of supplements
        self.food_item = interaction_data.get('foodItem')
        self.interaction_type = interaction_data.get('interactionType')
        self.effect = interaction_data.get('effect')
        self.description = interaction_data.get('description')
        self.recommendation = interaction_data.get('recommendation')
        self.sources = interaction_data.get('sources', [])  # List of sources
        self.created_at = interaction_data.get('createdAt')
        self.updated_at = interaction_data.get('updatedAt')
        self.deleted_at = interaction_data.get('deletedAt')

    def get_supplement_names(self):
        """
        Returns a list of supplement names from the supplements array.
        Handles cases where the name is null or missing.
        """
        return [supplement.get('name') for supplement in self.supplements if supplement.get('name')]

    def get_supplement_ids(self):
        """
        Returns a list of supplement IDs from the supplements array.
        Handles cases where the supplementId is null or missing.
        """
        return [supplement.get('supplementId') for supplement in self.supplements if supplement.get('supplementId')]
    
    def validate_data(self, interaction_data: dict):
        """Validate the interaction data"""
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in interaction_data or not interaction_data[field]:
                raise ValueError(f"Missing required field: {field}")
        # Validate effect
        if 'effect' in interaction_data:
            if interaction_data['effect'] not in self.VALID_EFFECTS:
                raise ValueError(f"Invalid effect. Must be one of: {', '.join(self.VALID_EFFECTS)}")
        # Validate interaction type
        if 'interactionType' in interaction_data:
            if interaction_data['interactionType'] not in self.VALID_INTERACTION_TYPES:
                raise ValueError(f"Invalid interaction type. Must be one of: {', '.join(self.VALID_INTERACTION_TYPES)}")
        
        # Validate supplements
        if 'supplements' in interaction_data:
            if not isinstance(interaction_data['supplements'], list) or len(interaction_data['supplements']) < 1:
                raise ValueError("Supplements must be a non-empty list")
                
            # If it's a supplement-supplement interaction, there should be at least 2 supplements
            if interaction_data['interactionType'] == 'Supplement-Supplement' and len(interaction_data['supplements']) < 2:
                raise ValueError("Supplement-Supplement interactions must have at least 2 supplements")
    
    def to_dict(self):
        """Convert interaction to dictionary"""
        result = {
            "supplements": self.supplements,
            "interactionType": self.interaction_type,
            "effect": self.effect,
            "description": self.description,
            "recommendation": self.recommendation,
            "sources": self.sources,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
        
        # Include optional fields if they exist
        if self._id:
            result["_id"] = str(self._id)
            
        if self.interaction_id:
            result["interactionId"] = self.interaction_id
            
        if self.food_item:
            result["foodItem"] = self.food_item

            
        return result
    
    @staticmethod
    def create(interaction_data: dict):
        """Create a new interaction"""
        # Validate data
        interaction = Interaction(interaction_data)
        interaction.validate_data(interaction_data)
        
        # Add timestamps
        now = datetime.now().isoformat()
        interaction_data['createdAt'] = now
        interaction_data['updatedAt'] = now
        interaction_data['interactionId'] = f"INT{str(datetime.now().timestamp()).replace('.', '')}"
        interaction_data['deletedAt'] = None
        # Insert into database
        db = get_db()
        
        result = db.Interactions.insert_one(interaction_data)
        
        if not result.inserted_id:
            raise ValueError("Failed to create interaction")
            
        # Return the created interaction
        created_data = interaction_data.copy()
        created_data['_id'] = result.inserted_id
        return Interaction(created_data)
    
    @staticmethod
    def find_by_id(_id):
        """Find an interaction by ID"""
        db = get_db()
        try:
            # Convert string ID to ObjectId if necessary
            if isinstance(_id, str):
                _id = ObjectId(_id)
                
            # Find interaction
            interaction = db.Interactions.find_one({'_id': _id, 'deletedAt': None})
            return Interaction(interaction) if interaction else None
        except Exception as e:
            raise ValueError(f"Error finding interaction: {e}")
    
    @staticmethod
    def find_all(query=None):
        """Find all interactions matching a query"""
        db = get_db()
        try:
            # Default query filters out deleted interactions
            if query is None:
                query = {}
            query['deletedAt'] = None
            
            # Find interactions
            interactions = list(db.Interactions.find(query))
            return [Interaction(interaction) for interaction in interactions]
        except Exception as e:
            raise ValueError(f"Error finding interactions: {e}")
    
    @staticmethod
    def update(_id, update_data):
        """Update an interaction"""
        db = get_db()
        try:
            # Convert string ID to ObjectId if necessary
            if isinstance(_id, str):
                _id = ObjectId(_id)
                
            # Check if interaction exists
            existing = db.Interactions.find_one({'_id': _id, 'deletedAt': None})
            if not existing:
                raise ValueError(f"Interaction not found with ID: {_id}")
                
            # Update timestamp
            update_data['updatedAt'] = datetime.now().isoformat()
            
            # Validate the update
            interaction = Interaction({**existing, **update_data})
            interaction.validate_data({**existing, **update_data})
            
            # Update in database
            db.Interactions.update_one({'_id': _id}, {'$set': update_data})
            
            # Return updated interaction
            updated = db.Interactions.find_one({'_id': _id})
            return Interaction(updated)
        except Exception as e:
            raise ValueError(f"Error updating interaction: {e}")
    
    @staticmethod
    def delete(_id, soft_delete=True):
        """Delete an interaction"""
        db = get_db()
        try:
            # Convert string ID to ObjectId if necessary
            if isinstance(_id, str):
                _id = ObjectId(_id)
                
            # Check if interaction exists
            existing = db.Interactions.find_one({'_id': _id, 'deletedAt': None})
            if not existing:
                return None
                
            if soft_delete:
                # Soft delete
                db.Interactions.update_one(
                    {'_id': _id},
                    {'$set': {'deletedAt': datetime.now().isoformat()}}
                )
                updated = db.Interactions.find_one({'_id': _id})
                return Interaction(updated)
            else:
                # Hard delete
                db.Interactions.delete_one({'_id': _id})
                return Interaction(existing)
        except Exception as e:
            raise ValueError(f"Error deleting interaction: {e}")
    
    # @staticmethod
    # def check_interactions(supplement_ids=None, food_items=None, medications=None):
    #     """Check for interactions between supplements, food items, and medications"""
    #     db = get_db()
    #     interactions = []
        
    #     try:
    #         # Search for supplement-supplement interactions
    #         if supplement_ids and len(supplement_ids) > 1:
    #             # Find interactions where at least 2 of the provided supplements are involved
    #             # Using MongoDB's $elemMatch to match array elements
    #             supp_interactions = list(db.Interactions.find({
    #                 'interactionType': 'Supplement-Supplement',
    #                 'deletedAt': None,
    #                 'supplements.supplementId': {'$in': supplement_ids}
    #             }))
                
    #             # Verify multiple supplements in the list match our criteria
    #             for interaction in supp_interactions:
    #                 interaction_supp_ids = [s.get('supplementId') for s in interaction.get('supplements', [])]
    #                 matching_ids = [sid for sid in supplement_ids if sid in interaction_supp_ids]
                    
    #                 # Only include if at least 2 supplements match
    #                 if len(matching_ids) >= 2:
    #                     interactions.append(Interaction(interaction))
            
    #         # Search for supplement-food interactions
    #         if supplement_ids and food_items:
    #             for food_item in food_items:
    #                 food_interactions = list(db.Interactions.find({
    #                     'interactionType': 'Supplement-Food',
    #                     'deletedAt': None,
    #                     'foodItem': food_item,
    #                     'supplements.supplementId': {'$in': supplement_ids}
    #                 }))
                    
    #                 for interaction in food_interactions:
    #                     interactions.append(Interaction(interaction))
            
    #         # Search for supplement-medication interactions
    #         if supplement_ids and medications:
    #             for medication in medications:
    #                 med_interactions = list(db.Interactions.find({
    #                     'interactionType': 'Supplement-Medication',
    #                     'deletedAt': None,
    #                     'medication': medication,
    #                     'supplements.supplementId': {'$in': supplement_ids}
    #                 }))
                    
    #                 for interaction in med_interactions:
    #                     interactions.append(Interaction(interaction))
                        
    #         return interactions
    #     except Exception as e:
    #         raise ValueError(f"Error checking interactions: {e}")
            
    # @staticmethod
    # def get_supplement_interactions(supplement_id):
    #     """Get all interactions for a specific supplement"""
    #     db = get_db()
    #     try:
    #         # Find interactions involving this supplement
    #         interactions = list(db.Interactions.find({
    #             'supplements.supplementId': supplement_id,
    #             'deletedAt': None
    #         }))
    #         return [Interaction(interaction) for interaction in interactions]
    #     except Exception as e:
    #         raise ValueError(f"Error getting supplement interactions: {e}")