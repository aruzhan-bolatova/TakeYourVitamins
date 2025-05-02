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
from app.models.supplement import Supplement
from app.routes.supplements import bp as supplements_bp
from app.models.interaction import Interaction

class TestSupplementRoutes(unittest.TestCase):

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
        self.admin_user_id = str(ObjectId())
        
        # Create access tokens
        self.access_token = create_access_token(identity=self.user_id)
        self.admin_access_token = create_access_token(identity=self.admin_user_id)
        self.headers = {'Authorization': f'Bearer {self.access_token}'}
        self.admin_headers = {'Authorization': f'Bearer {self.admin_access_token}'}

        # Register blueprint
        self.app.register_blueprint(supplements_bp)

        # Create dummy supplement data
        self.supplement_id = str(ObjectId())
        self.supplement_data = {
            "name": "Vitamin D",
            "aliases": ["Cholecalciferol", "Vitamin D3"],
            "description": "Essential for calcium absorption and bone health.",
            "category": "Vitamins"
        }

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    @patch('app.routes.supplements.Supplement.search')
    def test_get_supplements_success(self, mock_search):
        """Test getting supplements successfully."""
        # Configure mock
        mock_supp = MagicMock()
        mock_supp.to_dict.return_value = self.supplement_data
        mock_search.return_value = [mock_supp]

        # Make request
        response = self.client.get('/api/supplements/')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        
        # Verify mock was called correctly
        mock_search.assert_called_once_with('', field='name')

    @patch('app.routes.supplements.Supplement.search')
    def test_get_supplements_with_search(self, mock_search):
        """Test getting supplements with search query."""
        # Configure mock
        mock_supp = MagicMock()
        mock_supp.to_dict.return_value = self.supplement_data
        mock_search.return_value = [mock_supp]

        # Make request
        response = self.client.get('/api/supplements/?search=vitamin')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        
        # Verify mock was called correctly
        mock_search.assert_called_once_with('vitamin', field='name')

    @patch('app.routes.supplements.Supplement.find_by_id')
    def test_get_supplement_by_id_success(self, mock_find_by_id):
        """Test getting a supplement by ID successfully."""
        # Configure mock
        mock_supp = MagicMock()
        mock_supp.to_dict.return_value = self.supplement_data
        mock_find_by_id.return_value = mock_supp

        # Make request
        response = self.client.get(f'/api/supplements/{self.supplement_id}')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, self.supplement_data)
        
        # Verify mock was called correctly
        mock_find_by_id.assert_called_once()

    def test_get_supplement_by_id_invalid_id(self):
        """Test getting a supplement with an invalid ID."""
        # Make request with invalid ID
        response = self.client.get('/api/supplements/invalid-id')
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid ID format')

    @patch('app.routes.supplements.Supplement.find_by_id')
    def test_get_supplement_by_id_not_found(self, mock_find_by_id):
        """Test getting a supplement that doesn't exist."""
        # Configure mock
        mock_find_by_id.return_value = None

        # Make request
        response = self.client.get(f'/api/supplements/{self.supplement_id}')
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Supplement not found')

    @patch('app.routes.supplements.Supplement.autocomplete')
    def test_autocomplete_supplements_success(self, mock_autocomplete):
        """Test supplement autocomplete successfully."""
        # Configure mock
        mock_autocomplete.return_value = [
            {"id": self.supplement_id, "name": "Vitamin D"}
        ]

        # Make request
        response = self.client.get('/api/supplements/autocomplete?search=vit')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Vitamin D")
        
        # Verify mock was called correctly
        mock_autocomplete.assert_called_once_with('vit')

    def test_autocomplete_supplements_empty_query(self):
        """Test supplement autocomplete with empty query."""
        # Make request without search query
        response = self.client.get('/api/supplements/autocomplete')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

    @patch('app.routes.supplements.get_db')
    def test_get_interactions_by_supplement_success(self, mock_get_db):
        """Test getting interactions by supplement ID successfully."""
        # Create mock database and cursor
        mock_db = MagicMock()
        mock_interactions_collection = MagicMock()
        mock_db.Interactions = mock_interactions_collection
        mock_get_db.return_value = mock_db
        
        # Mock the find method to return a list of interactions
        mock_cursor = [
            {
                "_id": ObjectId(),
                "interactionType": "Supplement-Supplement",
                "supplements": [
                    {"supplementId": str(self.supplement_id), "name": "Vitamin D"},
                    {"supplementId": "another-id", "name": "Calcium"}
                ],
                "effect": "Enhances Absorption"
            },
            {
                "_id": ObjectId(),
                "interactionType": "Supplement-Food",
                "supplements": [
                    {"supplementId": str(self.supplement_id), "name": "Vitamin D"}
                ],
                "foodItem": "Dairy",
                "effect": "Enhances Absorption"
            }
        ]
        mock_interactions_collection.find.return_value = mock_cursor

        # Make request
        response = self.client.get(f'/api/supplements/by-supplement/{self.supplement_id}')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify the data structure
        self.assertIn('supplementSupplementInteractions', data)
        self.assertIn('supplementFoodInteractions', data)
        self.assertEqual(len(data['supplementSupplementInteractions']), 1)
        self.assertEqual(len(data['supplementFoodInteractions']), 1)
        
        # Verify the find method was called with correct arguments
        mock_interactions_collection.find.assert_called_once_with({
            "supplements": {
                "$elemMatch": {"supplementId": str(self.supplement_id)}
            }
        })

    def test_get_interactions_by_supplement_invalid_id(self):
        """Test getting interactions with an invalid supplement ID."""
        # Make request with invalid ID
        response = self.client.get('/api/supplements/by-supplement/invalid-id')
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid supplement ID format')

    @patch('app.routes.supplements.get_db')
    def test_get_interactions_by_supplement_db_error(self, mock_get_db):
        """Test getting interactions when a database error occurs."""
        # Configure mock to raise an exception
        mock_get_db.side_effect = Exception("Database connection error")

        # Make request
        response = self.client.get(f'/api/supplements/by-supplement/{self.supplement_id}')
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('details', data)
        self.assertEqual(data['error'], 'An error occurred while fetching interactions')

    @patch('app.routes.supplements.Supplement')
    @patch('app.routes.supplements.get_db')
    def test_create_supplement_success(self, mock_get_db, mock_supplement_class):
        """Test creating a supplement successfully."""
        # Configure mocks for Supplement validation
        mock_instance = MagicMock()
        mock_instance.to_dict.return_value = self.supplement_data
        mock_supplement_class.return_value = mock_instance
        
        # Configure DB mock
        mock_db = MagicMock()
        mock_supplements_collection = MagicMock()
        mock_db.Supplements = mock_supplements_collection
        mock_get_db.return_value = mock_db
        
        # Mock the insert_one method to return a successful result
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId()
        mock_supplements_collection.insert_one.return_value = mock_result

        # Make request
        response = self.client.post(
            '/api/supplements/',
            json=self.supplement_data,
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Supplement created successfully')
        self.assertIn('_id', data)
        
        # Verify insert_one was called
        mock_supplements_collection.insert_one.assert_called_once()

    def test_create_supplement_missing_json(self):
        """Test creating a supplement with missing JSON."""
        # Make request without JSON
        response = self.client.post(
            '/api/supplements/',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Missing JSON in request')

    def test_create_supplement_empty_data(self):
        """Test creating a supplement with empty data."""
        # Make request with empty JSON
        response = self.client.post(
            '/api/supplements/',
            json={},
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Empty supplement data')

    @patch('app.routes.supplements.Supplement')
    def test_create_supplement_validation_error(self, mock_supplement_class):
        """Test creating a supplement with validation error."""
        # Configure mock to raise a ValueError during validation
        mock_instance = MagicMock()
        mock_instance.validate_data.side_effect = ValueError("Required field missing")
        mock_supplement_class.return_value = mock_instance

        # Make request
        response = self.client.post(
            '/api/supplements/',
            json=self.supplement_data,
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Required field missing')

    @patch('app.routes.supplements.Supplement.update')
    def test_update_supplement_success(self, mock_update):
        """Test updating a supplement successfully."""
        # Configure mock
        mock_update.return_value = True

        # Make request
        response = self.client.put(
            f'/api/supplements/{self.supplement_id}',
            json={"description": "Updated description"},
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Supplement updated successfully')
        
        # Verify update was called with correct arguments
        mock_update.assert_called_once_with(ObjectId(self.supplement_id), {"description": "Updated description"})

    def test_update_supplement_invalid_id(self):
        """Test updating a supplement with an invalid ID."""
        # Make request with invalid ID
        response = self.client.put(
            '/api/supplements/invalid-id',
            json={"description": "Updated description"},
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('details', data)

    @patch('app.routes.supplements.Supplement.update')
    def test_update_supplement_not_found(self, mock_update):
        """Test updating a supplement that doesn't exist."""
        # Configure mock to raise a ValueError
        mock_update.side_effect = ValueError("Supplement not found")

        # Make request
        response = self.client.put(
            f'/api/supplements/{self.supplement_id}',
            json={"description": "Updated description"},
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Supplement not found')

    @patch('app.routes.supplements.Supplement.delete')
    def test_delete_supplement_success(self, mock_delete):
        """Test deleting a supplement successfully."""
        # Configure mock
        mock_delete.return_value = True

        # Make request
        response = self.client.delete(
            f'/api/supplements/{self.supplement_id}',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Supplement deleted successfully')
        
        # Verify delete was called with correct arguments
        mock_delete.assert_called_once_with(ObjectId(self.supplement_id), soft_delete=True)

    def test_delete_supplement_invalid_id(self):
        """Test deleting a supplement with an invalid ID."""
        # Make request with invalid ID
        response = self.client.delete(
            '/api/supplements/invalid-id',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('details', data)

    @patch('app.routes.supplements.Supplement.delete')
    def test_delete_supplement_not_found(self, mock_delete):
        """Test deleting a supplement that doesn't exist."""
        # Configure mock to return False (not found)
        mock_delete.return_value = False

        # Make request
        response = self.client.delete(
            f'/api/supplements/{self.supplement_id}',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Supplement not found')

    @patch('app.routes.supplements.Supplement.delete')
    def test_delete_supplement_hard_delete(self, mock_delete):
        """Test hard deleting a supplement."""
        # Configure mock
        mock_delete.return_value = True

        # Make request with soft=false query parameter
        response = self.client.delete(
            f'/api/supplements/{self.supplement_id}?soft=false',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        
        # Verify delete was called with soft_delete=False
        mock_delete.assert_called_once_with(ObjectId(self.supplement_id), soft_delete=False)


if __name__ == '__main__':
    unittest.main() 