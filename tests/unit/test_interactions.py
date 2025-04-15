import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from bson.objectid import ObjectId

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.interaction import Interaction


class TestInteractions(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        
        # Mock ObjectId
        self.test_id = "507f5a99acf86cd799439011"
        self.test_object_id = ObjectId(self.test_id)
        
        # Sample interaction data
        self.test_interaction_data = {
            "_id": self.test_id,
            "interactionId": "INT799",
            "supplementId1": "SUPP798",
            "supplementId2": "SUPP700",
            "foodItem": None,
            "interactionType": "negative",
            "effect": "Reduces absorption",
            "description": "Supplement A reduces the absorption of Supplement B.",
            "severity": "moderate",
            "recommendation": "Take supplements at least 2 hours apart.",
            "sources": [],
            "updatedAt": None
        }
        
        # Mock interaction object
        self.mock_interaction = MagicMock()
        self.mock_interaction._id = self.test_id
        self.mock_interaction.to_dict.return_value = self.test_interaction_data
    
    def tearDown(self):
        """Tear down test fixtures after each test method is run."""
        self.app_context.pop()
    
    # GET /api/interactions/<interaction_id> - Get a specific interaction
    @patch('app.models.interaction.Interaction.find_by_supplement')
    def test_get_interaction_by_supplement_id_success(self, mock_find_by_supplement):
        """Test getting interactions by supplement ID successfully."""
        # Setup mock
        mock_find_by_supplement.return_value = [self.mock_interaction]
        
        # Make request
        response = self.client.get(f'/api/interactions/supplements/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["interactionId"], "INT001")
        
        # Verify mock was called with correct ID
        mock_find_by_supplement.assert_called_once_with(self.test_id)
    
    @patch('app.models.interaction.Interaction.find_by_supplement')
    def test_get_interaction_by_supplement_id_not_found(self, mock_find_by_supplement):
        """Test getting interactions by supplement ID when no interactions are found."""
        # Setup mock to return an empty list
        mock_find_by_supplement.return_value = []
        
        # Make request
        response = self.client.get(f'/api/interactions/supplements/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["results"]), 0)
    
    # POST /api/interactions/ - Create a new interaction
    @patch('app.routes.interactions.get_db')
    def test_create_interaction_success(self, mock_get_db):
        """Test creating a new interaction successfully."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_supplements_collection = MagicMock()
        mock_interactions_collection = MagicMock()
        mock_db.Supplements = mock_supplements_collection
        mock_db.Interactions = mock_interactions_collection
        mock_get_db.return_value = mock_db

        # Mock insert_one for supplements
        mock_supplement_result = MagicMock()
        mock_supplement_result.inserted_id = ObjectId()
        mock_supplements_collection.insert_one.return_value = mock_supplement_result

        # Add supplements SUPP797 and SUPP796
        supplement_1 = {
            "supplementId": "SUPP797",
            "name": "Supplement C",
            "description": "Description for Supplement C",
            "category": "Category C"
        }
        supplement_2 = {
            "supplementId": "SUPP796",
            "name": "Supplement D",
            "description": "Description for Supplement D",
            "category": "Category D"
        }
        mock_supplements_collection.insert_one(supplement_1)
        mock_supplements_collection.insert_one(supplement_2)

        # Mock insert_one for interaction
        mock_interaction_result = MagicMock()
        mock_interaction_result.inserted_id = self.test_object_id
        mock_interactions_collection.insert_one.return_value = mock_interaction_result

        # Make request to create interaction
        new_interaction = {
            "interactionId": "INT702",
            "supplementId1": "SUPP797",
            "supplementId2": "SUPP796",
            "interactionType": "negative",
            "effect": "Inhibits absorption",
            "description": "Supplement C inhibits the absorption of Supplement D.",
            "severity": "high",
            "recommendation": "Avoid taking these supplements together.",
            "sources": ["Source A", "Source B"]
        }

        response = self.client.post(
            '/api/interactions/',
            data=json.dumps(new_interaction),
            content_type='application/json'
        )

        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["message"], "Interaction created successfully")
        self.assertIn("_id", data)

        # Verify mock calls
        mock_supplements_collection.insert_one.assert_any_call(supplement_1)
        mock_supplements_collection.insert_one.assert_any_call(supplement_2)
        mock_interactions_collection.insert_one.assert_called_once_with(new_interaction)
        
    def test_create_interaction_missing_fields(self):
        """Test creating an interaction with missing required fields."""
        # Make request with missing interactionType
        incomplete_data = {
            "interactionId": "INT703",
            "supplementId1": "SUPP005"
        }
        
        response = self.client.post(
            '/api/interactions/',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required field", data["error"])
    
    # PUT /api/interactions/<interaction_id> - Update an interaction
    @patch('app.models.interaction.Interaction.update')
    def test_update_interaction_success(self, mock_update):
        """Test updating an interaction successfully."""
        # Make request
        update_data = {
            "description": "Updated description for the interaction."
        }
        
        response = self.client.put(
            f'/api/interactions/{self.test_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Interaction updated successfully")
        
        # Verify mock was called
        mock_update.assert_called_once_with(self.test_object_id, update_data)
    
    # DELETE /api/interactions/<interaction_id> - Delete an interaction
    @patch('app.models.interaction.Interaction.delete')
    def test_delete_interaction_success(self, mock_delete):
        """Test deleting an interaction successfully."""
        # Setup mock
        mock_delete.return_value = True
        
        # Make request
        response = self.client.delete(f'/api/interactions/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Interaction deleted successfully")
        
        # Verify mock was called
        mock_delete.assert_called_once_with(self.test_object_id, soft_delete=True)



    # Test for check_interactions
    @patch('app.models.interaction.Interaction.check_interactions')
    def test_check_interactions(self, mock_check_interactions):
        """Test checking interactions between supplements and foods."""
        # Setup mock
        mock_check_interactions.return_value = [self.test_interaction_data]

        # Mock intake and food lists
        intake_list = [{"supplementId": "SUPP001"}]
        food_list = ["Dairy products"]

        # Make request
        response = self.client.get(
            '/api/interactions/check',
            query_string={"intake_list": json.dumps(intake_list), "food_list": json.dumps(food_list)}
        )

        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["interactions"]), 1)
        self.assertEqual(data["interactions"][0]["interactionId"], "INT001")

        # Verify mock was called
        mock_check_interactions.assert_called_once_with(intake_list, food_list)

    # Test for generate_alerts_from_list
    @patch('app.models.interaction.Interaction.generate_alerts')
    def test_generate_alerts_from_list(self, mock_generate_alerts):
        """Test generating alerts based on intake and food lists."""
        # Setup mock
        mock_generate_alerts.return_value = [
            {
                "type": "negative",
                "message": "Supplement A reduces the absorption of Supplement B.",
                "severity": "moderate",
                "recommendation": "Take supplements at least 2 hours apart."
            }
        ]

        # Mock intake and food lists
        intake_list = [{"supplementId": "SUPP001"}]
        food_list = ["Dairy products"]

        # Make request
        response = self.client.post(
            '/api/interactions/check-interactions',
            data=json.dumps({"intake_list": intake_list, "food_list": food_list}),
            content_type='application/json'
        )

        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["alerts"]), 1)
        self.assertEqual(data["alerts"][0]["type"], "negative")

        # Verify mock was called
        mock_generate_alerts.assert_called_once_with(intake_list, food_list)

    # Test for get_interactions_by_supplement_ID
    @patch('app.models.interaction.Interaction.find_by_supplement')
    def test_get_interactions_by_supplement_ID(self, mock_find_by_supplement):
        """Test getting interactions by supplement ID."""
        # Setup mock
        mock_find_by_supplement.return_value = [self.test_interaction_data]

        # Make request
        response = self.client.get(f'/api/supplements/{self.test_id}/interactions')

        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["interactionId"], "INT001")

        # Verify mock was called
        mock_find_by_supplement.assert_called_once_with(self.test_id)



if __name__ == '__main__':
    unittest.main()