from app.db.db import get_database as get_db

class Supplement:
    def __init__(self, supplement_data: dict):
        self.supplement_id = supplement_data.get('supplementId')
        self.name = supplement_data.get('name')
        self.aliases = supplement_data.get('aliases')
        self.description = supplement_data.get('description')
        self.intake_practices = supplement_data.get('intakePractices')
        self.scientific_details = supplement_data.get('scientificDetails')
        self.category = supplement_data.get('category')
        self.updated_at = supplement_data.get('updatedAt')

    @staticmethod
    def search(search_query: str):
        db = get_db()
        query = {'name': {'$regex': search_query, '$options': 'i'}} if search_query else {}
        return [Supplement(s) for s in db.Supplements.find(query)]

    @staticmethod
    def find_by_id(supplement_id: str):
        db = get_db()
        supplement = db.Supplements.find_one({'supplementId': supplement_id})
        return Supplement(supplement) if supplement else None