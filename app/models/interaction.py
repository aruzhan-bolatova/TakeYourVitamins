class Interaction:
    def __init__(self, interaction_data: dict):
        self.interaction_id = interaction_data.get('interactionId')
        self.supplements = interaction_data.get('supplements', [])  # List of supplements
        self.food_item = interaction_data.get('foodItem')
        self.interaction_type = interaction_data.get('interactionType')
        self.effect = interaction_data.get('effect')
        self.description = interaction_data.get('description')
        self.severity = interaction_data.get('severity')
        self.recommendation = interaction_data.get('recommendation')
        self.sources = interaction_data.get('sources', [])  # List of sources
        self.updated_at = interaction_data.get('updatedAt')

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