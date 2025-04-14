from app.db.db import get_database as get_db
from datetime import datetime, timezone
from app.models.supplement import Supplement

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
    def get_supplement_name(supplement_id: str):
        """Get the name of a supplement by its ID"""
        supplement = Supplement.find_by_id(supplement_id)
        if not supplement:
            raise ValueError(f"Supplement with ID {supplement_id} not found")
        return supplement.name

    @staticmethod
    def check_interactions(intake_list: list, food_items: list):
        db = get_db()
        alerts = []
        supplement_ids = [item['supplementId'] for item in intake_list]

        # Step 1: Fetch all supplement names in one query
        supplements = list(db.Supplements.find(
            {'supplementId': {'$in': supplement_ids}},
            {'supplementId': 1, 'name': 1, '_id': 0}
        ))
        supplement_name_map = {s['supplementId']: s['name'] for s in supplements}
        # Validate all supplement IDs exist
        missing_ids = [sid for sid in supplement_ids if sid not in supplement_name_map]
        if missing_ids:
            raise ValueError(f"Supplements not found: {missing_ids}")

        # Step 2: Fetch all relevant interactions in one query
        interactions = list(db.Interactions.find({
            '$or': [
                {'supplementId1': {'$in': supplement_ids}},
                {'supplementId2': {'$in': supplement_ids}}
            ]
        }))

        # Step 3: Process interactions and generate alerts
        seen_interactions = set()  # To avoid duplicates
        for i in interactions:
            interaction_key = None
            alert = None

            # Supplement-supplement interaction
            if i['supplementId2'] and i['supplementId2'] in supplement_ids:
                # Normalize to avoid duplicates (e.g., Iron-Zinc and Zinc-Iron)
                supp_ids = sorted([i['supplementId1'], i['supplementId2']])
                interaction_key = f"supp:{supp_ids[0]}:{supp_ids[1]}"
                if interaction_key in seen_interactions:
                    continue
                seen_interactions.add(interaction_key)

                supp1_name = supplement_name_map[i['supplementId1']]
                supp2_name = supplement_name_map[i['supplementId2']]
                alert = {
                    'type': i['interactionType'],
                    'supplement1': {'id': i['supplementId1'], 'name': supp1_name},
                    'supplement2': {'id': i['supplementId2'], 'name': supp2_name},
                    'message': i['description'],
                    'severity': i['severity'],
                    'recommendation': i['recommendation']
                }

            # Supplement-food interaction
            elif i['foodItem'] in food_items:
                interaction_key = f"food:{i['supplementId1']}:{i['foodItem']}"
                if interaction_key in seen_interactions:
                    continue
                seen_interactions.add(interaction_key)

                supp_name = supplement_name_map[i['supplementId1']]
                alert = {
                    'type': i['interactionType'],
                    'supplement': {'id': i['supplementId1'], 'name': supp_name},
                    'food': i['foodItem'],
                    'message': i['description'],
                    'severity': i['severity'],
                    'recommendation': i['recommendation']
                }

            if alert:
                alerts.append(alert)

        return alerts