from app.db.db import get_database as get_db
from datetime import datetime, UTC

class Interaction:
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
        alerts = []
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
                    alerts.append({
                        'type': i['interactionType'],
                        'message': i['description'],
                        'severity': i['severity'],
                        'recommendation': i['recommendation']
                    })
        return alerts