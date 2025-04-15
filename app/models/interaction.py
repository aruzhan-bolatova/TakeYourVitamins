from app.db.db import get_database as get_db
from datetime import datetime, timezone

class Interaction:
    REQUIRED_FIELDS = ['supplementId1', 'interactionType']
    def __init__(self, interaction_data: dict):
        self.interaction_id = interaction_data.get('interactionId')
        self.supplement_id1 = interaction_data.get('supplementId1')
        self.supplement_id2 = interaction_data.get('supplementId2')
        self.food_item = interaction_data.get('foodItem')
        self.interaction_type = interaction_data.get('interactionType')
        self.effect = interaction_data.get('effect')
        self.description = interaction_data.get('description')
        self.severity = interaction_data.get('severity')
        self.recommendation = interaction_data.get('recommendation')
        self.sources = interaction_data.get('sources')
        self.updated_at = interaction_data.get('updatedAt')

    def validate_data(self, interaction_data):
        for field in self.REQUIRED_FIELDS:
            if field not in interaction_data or not interaction_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        has_supplement_id2 = bool(interaction_data.get('supplementId2'))
        has_food_item = bool(interaction_data.get('foodItem'))

        if has_supplement_id2 == has_food_item:  
            raise ValueError("Exactly one of 'supplementId2' or 'foodItem' must be provided.")

        db = get_db()
        # Validate supplementId1 exists in the database
        supplement_id1 = interaction_data.get('supplementId1')
        if not db.Supplements.find_one({'supplementId': supplement_id1}):
            raise ValueError(f"Supplement with ID '{supplement_id1}' does not exist in the database.")
        
        # Validate supplementId2 exists in the database (if provided)
        if has_supplement_id2:
            supplement_id2 = interaction_data.get('supplementId2')
            if not db.Supplements.find_one({'supplementId': supplement_id2}):
                raise ValueError(f"Supplement with ID '{supplement_id2}' does not exist in the database.")


    def to_dict(self):
        return {
            "interactionId": self.interaction_id,
            "supplementId1": self.supplement_id1,
            "supplementId2": self.supplement_id2,
            "foodItem": self.food_item,
            "interactionType": self.interaction_type,
            "effect": self.effect,
            "description": self.description,
            "severity": self.severity,
            "recommendation": self.recommendation,
            "sources": self.sources,
            "updatedAt": self.updated_at
        }


    @staticmethod
    def find_by_supplement(supplement_id: str):
        db = get_db()
        interactions = db.Interactions.find({
            '$or': [
                {'supplementId1': supplement_id},
                {'supplementId2': supplement_id}
            ]
        })
        return [Interaction(i) for i in interactions]

    @staticmethod
    def check_interactions(intake_list: list, food_items: list):
        db = get_db()
        results=[]
        supplement_ids = [item['supplementId'] for item in intake_list]
        for supplement_id in supplement_ids:
            interactions = db.Interactions.find({
                '$or': [
                            {'supplementId1': supplement_id},
                            {'supplementId2': supplement_id}
                        ]
            })
            for i in interactions:
                if i['foodItem'] in food_items or (i['supplementId2'] and i['supplementId2'] in supplement_ids):
                        results.append(i)
        return results
    

    @staticmethod
    def generate_alerts(intake_list: list, food_items: list):
        db = get_db()
        alerts = []
        supplement_ids = [item['supplementId'] for item in intake_list]
        for supplement_id in supplement_ids:
            interactions = db.Interactions.find({
                '$and': [
                    {
                        '$or': [
                            {'supplementId1': supplement_id},
                            {'supplementId2': supplement_id}
                        ]
                    },
                    {'interactionType': 'negative'}
                ]
            })
            for i in interactions:
                if i['foodItem'] in food_items or (i['supplementId2'] and i['supplementId2'] in supplement_ids):
                    alerts.append({
                        'type': i['interactionType'],
                        'message': i['description'],
                        'severity': i['severity'],
                        'recommendation': i['recommendation']
                    })
        return alerts
    

# Method to update an existing interaction
@staticmethod
def update(_id: str, interaction_data: dict):
    db = get_db()
    try:
        # Fetch the existing interaction
        existing_interaction = db.Interactions.find_one({'_id': _id})
        if not existing_interaction:
            raise ValueError(f"Interaction with ID {_id} not found.")
        
        # Merge the existing data with the new data
        updated_data = {**existing_interaction, **interaction_data}
        
        # Validate the merged data
        interaction = Interaction(updated_data)
        interaction.validate_data(updated_data)
        
        # Update the interaction in the database
        db.Interactions.update_one(
            {'_id': _id},
            {'$set': interaction_data}
        )
    except Exception as e:
        raise ValueError(f"Error updating interaction: {e}")

# Method to delete an interaction
@staticmethod
def delete(_id: str, soft_delete: bool = True):
    db = get_db()
    if soft_delete:
        # Perform a soft delete by setting a deletedAt timestamp
        result = db.Interactions.update_one(
            {'_id': _id},
            {'$set': {'deletedAt': datetime.now(timezone.utc).isoformat()}}
        )
    else:
        # Perform a hard delete by removing the document
        result = db.Interactions.delete_one({'_id': _id})
    return result.deleted_count > 0 if not soft_delete else result.modified_count > 0

