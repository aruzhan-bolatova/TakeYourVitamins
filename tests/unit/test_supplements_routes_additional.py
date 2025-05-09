import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_jwt_extended import create_access_token, JWTManager
from bson.objectid import ObjectId
import sys
import os
import json

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.routes.supplements import bp as supplements_bp
from app.models.supplement import Supplement

class TestSupplementsRoutesAdditional(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        self.client = self.app.test_client()
        self.jwt = JWTManager(self.app)

        # Push application context so create_access_token works
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create dummy user IDs
        self.user_id = str(ObjectId())
        
        # Create access tokens
        self.access_token = create_access_token(identity=self.user_id)
        self.headers = {'Authorization': f'Bearer {self.access_token}'}

        # Register blueprint
        self.app.register_blueprint(supplements_bp)

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    @patch('app.routes.supplements.Supplement.autocomplete')
    def test_autocomplete_supplements_with_search(self, mock_autocomplete):
        """Test autocomplete endpoint with a search query."""
        # Configure mock
        mock_autocomplete.return_value = [
            {"id": str(ObjectId()), "name": "Vitamin D"},
            {"id": str(ObjectId()), "name": "Vitamin D3"}
        ]

        # Make request
        response = self.client.get('/api/supplements/autocomplete?search=vita', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Vitamin D")
        
        # Verify mock was called correctly
        mock_autocomplete.assert_called_once_with('vita')

    @patch('app.routes.supplements.Supplement.autocomplete')
    def test_autocomplete_supplements_empty_search(self, mock_autocomplete):
        """Test autocomplete endpoint without a search query."""
        # Make request
        response = self.client.get('/api/supplements/autocomplete', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])
        
        # Verify mock was not called
        mock_autocomplete.assert_not_called()

    @patch('app.routes.supplements.Supplement.autocomplete')
    def test_autocomplete_supplements_exception(self, mock_autocomplete):
        """Test autocomplete endpoint with an exception."""
        # Configure mock
        mock_autocomplete.side_effect = Exception("Database error")

        # Make request
        response = self.client.get('/api/supplements/autocomplete?search=vita', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "An error occurred")
        self.assertEqual(data["details"], "Database error")
        
        # Verify mock was called correctly
        mock_autocomplete.assert_called_once_with('vita')

    @patch('app.routes.supplements.get_db')
    def test_get_interactions_by_supplement_success(self, mock_get_db):
        """Test getting interactions by supplement successfully."""
        # Configure mock database
        mock_db = MagicMock()
        mock_interactions_collection = MagicMock()
        mock_db.Interactions = mock_interactions_collection
        
        # Configure mock find method
        supplement_id = str(ObjectId())
        interactions = [
            {
                "_id": ObjectId(),
                "interactionType": "Supplement-Supplement",
                "supplements": [
                    {"supplementId": supplement_id, "name": "Vitamin D"},
                    {"supplementId": str(ObjectId()), "name": "Calcium"}
                ],
                "effect": "Enhances absorption"
            },
            {
                "_id": ObjectId(),
                "interactionType": "Supplement-Food",
                "supplements": [
                    {"supplementId": supplement_id, "name": "Vitamin D"}
                ],
                "foodItem": "Dairy",
                "effect": "Enhances absorption"
            }
        ]
        mock_interactions_collection.find.return_value = interactions
        mock_get_db.return_value = mock_db

        # Make request
        response = self.client.get(f'/api/supplements/by-supplement/{supplement_id}', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('supplementSupplementInteractions', data)
        self.assertIn('supplementFoodInteractions', data)
        self.assertEqual(len(data['supplementSupplementInteractions']), 1)
        self.assertEqual(len(data['supplementFoodInteractions']), 1)
        
        # Verify mock was called correctly
        mock_interactions_collection.find.assert_called_once_with({
            "supplements": {
                "$elemMatch": {"supplementId": supplement_id}
            }
        })

    def test_get_interactions_by_supplement_invalid_id(self):
        """Test getting interactions with an invalid supplement ID."""
        # Make request with invalid ID
        response = self.client.get('/api/supplements/by-supplement/invalid-id', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Invalid supplement ID format")

    @patch('app.routes.supplements.get_db')
    def test_get_interactions_by_supplement_exception(self, mock_get_db):
        """Test exception during interactions retrieval by supplement."""
        # Configure mock to raise an exception
        supplement_id = str(ObjectId())
        mock_get_db.side_effect = Exception("Database error")

        # Make request
        response = self.client.get(f'/api/supplements/by-supplement/{supplement_id}', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "An error occurred while fetching interactions")
        self.assertEqual(data["details"], "Database error")
        
        # Verify mock was called
        mock_get_db.assert_called_once()


if __name__ == '__main__':
    unittest.main() 