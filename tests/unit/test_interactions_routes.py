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
from app.models.interaction import Interaction
from app.routes.interactions import bp as interactions_bp

class TestInteractionsRoutes(unittest.TestCase):

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
        self.app.register_blueprint(interactions_bp)

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_success(self, mock_find_all):
        """Test successful retrieval of interactions."""
        # Configure mock
        mock_interaction = MagicMock()
        mock_interaction.to_dict.return_value = {"_id": str(ObjectId()), "effect": "Test effect"}
        mock_find_all.return_value = [mock_interaction]

        # Make request
        response = self.client.get('/api/interactions/', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["effect"], "Test effect")
        
        # Verify mock was called correctly
        mock_find_all.assert_called_once_with({})

    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_with_type(self, mock_find_all):
        """Test getting interactions with a specific type."""
        # Configure mock
        mock_interaction = MagicMock()
        mock_interaction.to_dict.return_value = {"_id": str(ObjectId()), "interactionType": "Supplement-Food"}
        mock_find_all.return_value = [mock_interaction]

        # Make request
        response = self.client.get('/api/interactions/?type=Supplement-Food', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["interactionType"], "Supplement-Food")
        
        # Verify mock was called correctly
        mock_find_all.assert_called_once_with({"interactionType": "Supplement-Food"})

    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_with_search_query(self, mock_find_all):
        """Test getting interactions with a search query."""
        # Configure mock
        mock_interaction = MagicMock()
        mock_interaction.to_dict.return_value = {"_id": str(ObjectId()), "effect": "May increase absorption"}
        mock_find_all.return_value = [mock_interaction]

        # Make request
        response = self.client.get('/api/interactions/?query=absorption', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["effect"], "May increase absorption")
        
        # Verify mock was called correctly
        expected_query = {
            "$or": [
                {"effect": {"$regex": "absorption", "$options": "i"}},
                {"description": {"$regex": "absorption", "$options": "i"}},
                {"recommendation": {"$regex": "absorption", "$options": "i"}}
            ]
        }
        mock_find_all.assert_called_once_with(expected_query)

    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_with_type_and_search(self, mock_find_all):
        """Test getting interactions with both type and search query."""
        # Configure mock
        mock_interaction = MagicMock()
        mock_interaction.to_dict.return_value = {
            "_id": str(ObjectId()), 
            "interactionType": "Supplement-Food",
            "effect": "May increase absorption"
        }
        mock_find_all.return_value = [mock_interaction]

        # Make request
        response = self.client.get('/api/interactions/?type=Supplement-Food&query=absorption', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["interactionType"], "Supplement-Food")
        
        # Verify mock was called correctly
        expected_query = {
            "interactionType": "Supplement-Food",
            "$or": [
                {"effect": {"$regex": "absorption", "$options": "i"}},
                {"description": {"$regex": "absorption", "$options": "i"}},
                {"recommendation": {"$regex": "absorption", "$options": "i"}}
            ]
        }
        mock_find_all.assert_called_once_with(expected_query)

    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_value_error(self, mock_find_all):
        """Test ValueError during interaction retrieval."""
        # Configure mock
        mock_find_all.side_effect = ValueError("Invalid query parameter")

        # Make request
        response = self.client.get('/api/interactions/', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Invalid query parameter")
        
        # Verify mock was called correctly
        mock_find_all.assert_called_once()

    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_exception(self, mock_find_all):
        """Test exception during interaction retrieval."""
        # Configure mock
        mock_find_all.side_effect = Exception("Database error")

        # Make request
        response = self.client.get('/api/interactions/', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Failed to get interactions")
        self.assertEqual(data["details"], "Database error")
        
        # Verify mock was called correctly
        mock_find_all.assert_called_once()

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.create')
    def test_create_interaction_success(self, mock_create, mock_is_admin):
        """Test successful creation of an interaction."""
        # Configure mocks
        mock_is_admin.return_value = True
        mock_interaction = MagicMock()
        mock_interaction._id = ObjectId()
        mock_create.return_value = mock_interaction
        
        interaction_data = {
            "interactionType": "Supplement-Supplement",
            "supplements": [
                {"supplementId": str(ObjectId()), "name": "Vitamin D"},
                {"supplementId": str(ObjectId()), "name": "Calcium"}
            ],
            "effect": "Enhances absorption"
        }

        # Make request
        response = self.client.post('/api/interactions/', json=interaction_data, headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Interaction created successfully")
        self.assertEqual(data["_id"], str(mock_interaction._id))
        
        # Verify mocks were called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_create.assert_called_once_with(interaction_data)

    @patch('app.routes.interactions.is_admin')
    def test_create_interaction_not_admin(self, mock_is_admin):
        """Test creation of an interaction by a non-admin user."""
        # Configure mock
        mock_is_admin.return_value = False
        
        interaction_data = {
            "interactionType": "Supplement-Supplement",
            "effect": "Enhances absorption"
        }

        # Make request
        response = self.client.post('/api/interactions/', json=interaction_data, headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Admin privileges required")
        
        # Verify mock was called correctly
        mock_is_admin.assert_called_once_with(self.user_id)

    @patch('app.routes.interactions.is_admin')
    def test_create_interaction_missing_json(self, mock_is_admin):
        """Test creation of an interaction with missing JSON data."""
        # Configure mock
        mock_is_admin.return_value = True

        # Make request without JSON
        response = self.client.post('/api/interactions/', headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Missing JSON in request")
        
        # Verify mock was called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.create')
    def test_create_interaction_validation_error(self, mock_create, mock_is_admin):
        """Test creation of an interaction with validation error."""
        # Configure mocks
        mock_is_admin.return_value = True
        mock_create.side_effect = ValueError("Missing required field")
        
        interaction_data = {
            "effect": "Enhances absorption"
            # Missing required fields
        }

        # Make request
        response = self.client.post('/api/interactions/', json=interaction_data, headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Missing required field")
        
        # Verify mocks were called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_create.assert_called_once_with(interaction_data)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.create')
    def test_create_interaction_exception(self, mock_create, mock_is_admin):
        """Test exception during interaction creation."""
        # Configure mocks
        mock_is_admin.return_value = True
        mock_create.side_effect = Exception("Database error")
        
        interaction_data = {
            "interactionType": "Supplement-Supplement",
            "effect": "Enhances absorption"
        }

        # Make request
        response = self.client.post('/api/interactions/', json=interaction_data, headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Failed to create interaction")
        self.assertEqual(data["details"], "Database error")
        
        # Verify mocks were called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_create.assert_called_once_with(interaction_data)

    @patch('app.routes.interactions.Interaction.find_by_id')
    def test_get_interaction_by_id_success(self, mock_find_by_id):
        """Test successful retrieval of an interaction by ID."""
        # Configure mock
        interaction_id = str(ObjectId())
        mock_interaction = MagicMock()
        mock_interaction.to_dict.return_value = {
            "_id": interaction_id,
            "interactionType": "Supplement-Supplement",
            "effect": "Enhances absorption"
        }
        mock_find_by_id.return_value = mock_interaction

        # Make request
        response = self.client.get(f'/api/interactions/{interaction_id}', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["_id"], interaction_id)
        self.assertEqual(data["effect"], "Enhances absorption")
        
        # Verify mock was called correctly
        mock_find_by_id.assert_called_once_with(interaction_id)

    @patch('app.routes.interactions.Interaction.find_by_id')
    def test_get_interaction_by_id_not_found(self, mock_find_by_id):
        """Test retrieval of a non-existent interaction."""
        # Configure mock
        interaction_id = str(ObjectId())
        mock_find_by_id.return_value = None

        # Make request
        response = self.client.get(f'/api/interactions/{interaction_id}', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Interaction not found")
        
        # Verify mock was called correctly
        mock_find_by_id.assert_called_once_with(interaction_id)

    def test_get_interaction_by_id_invalid_id(self):
        """Test retrieval of an interaction with an invalid ID format."""
        # Make request with invalid ID
        response = self.client.get('/api/interactions/invalid-id', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("not a valid ObjectId", data["error"])

    @patch('app.routes.interactions.Interaction.find_by_id')
    def test_get_interaction_by_id_exception(self, mock_find_by_id):
        """Test exception during interaction retrieval by ID."""
        # Configure mock
        interaction_id = str(ObjectId())
        mock_find_by_id.side_effect = Exception("Database error")

        # Make request
        response = self.client.get(f'/api/interactions/{interaction_id}', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Failed to get interaction")
        self.assertEqual(data["details"], "Database error")
        
        # Verify mock was called correctly
        mock_find_by_id.assert_called_once_with(interaction_id)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.update')
    def test_update_interaction_success(self, mock_update, mock_is_admin):
        """Test successful update of an interaction."""
        # Configure mocks
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        mock_interaction = MagicMock()
        mock_interaction._id = ObjectId(interaction_id)
        mock_update.return_value = mock_interaction
        
        update_data = {
            "effect": "Updated effect information"
        }

        # Make request
        response = self.client.put(f'/api/interactions/{interaction_id}', json=update_data, headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Interaction updated successfully")
        self.assertEqual(data["_id"], interaction_id)
        
        # Verify mocks were called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_update.assert_called_once_with(interaction_id, update_data)

    @patch('app.routes.interactions.is_admin')
    def test_update_interaction_not_admin(self, mock_is_admin):
        """Test update of an interaction by a non-admin user."""
        # Configure mock
        mock_is_admin.return_value = False
        interaction_id = str(ObjectId())
        
        update_data = {
            "effect": "Updated effect information"
        }

        # Make request
        response = self.client.put(f'/api/interactions/{interaction_id}', json=update_data, headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Admin privileges required")
        
        # Verify mock was called correctly
        mock_is_admin.assert_called_once_with(self.user_id)

    @patch('app.routes.interactions.is_admin')
    def test_update_interaction_missing_json(self, mock_is_admin):
        """Test update of an interaction with missing JSON data."""
        # Configure mock
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())

        # Make request without JSON
        response = self.client.put(f'/api/interactions/{interaction_id}', headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Missing JSON in request")
        
        # Verify mock was called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)

    @patch('app.routes.interactions.is_admin')
    def test_update_interaction_empty_data(self, mock_is_admin):
        """Test update of an interaction with empty update data."""
        # Configure mock
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())

        # Make request with empty JSON
        response = self.client.put(f'/api/interactions/{interaction_id}', json={}, headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "No update data provided")
        
        # Verify mock was called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.update')
    def test_update_interaction_validation_error(self, mock_update, mock_is_admin):
        """Test update of an interaction with validation error."""
        # Configure mocks
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        mock_update.side_effect = ValueError("Invalid data format")
        
        update_data = {
            "invalidField": "Value"
        }

        # Make request
        response = self.client.put(f'/api/interactions/{interaction_id}', json=update_data, headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Invalid data format")
        
        # Verify mocks were called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_update.assert_called_once_with(interaction_id, update_data)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.update')
    def test_update_interaction_exception(self, mock_update, mock_is_admin):
        """Test exception during interaction update."""
        # Configure mocks
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        mock_update.side_effect = Exception("Database error")
        
        update_data = {
            "effect": "Updated effect information"
        }

        # Make request
        response = self.client.put(f'/api/interactions/{interaction_id}', json=update_data, headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Failed to update interaction")
        self.assertEqual(data["details"], "Database error")
        
        # Verify mocks were called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_update.assert_called_once_with(interaction_id, update_data)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_success(self, mock_delete, mock_is_admin):
        """Test successful deletion of an interaction."""
        # Configure mocks
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        mock_interaction = MagicMock()
        mock_interaction._id = ObjectId(interaction_id)
        mock_delete.return_value = mock_interaction

        # Make request
        response = self.client.delete(f'/api/interactions/{interaction_id}', headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Interaction deleted successfully")
        self.assertEqual(data["_id"], interaction_id)
        
        # Verify mocks were called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_delete.assert_called_once_with(interaction_id, soft_delete=True)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_hard_delete(self, mock_delete, mock_is_admin):
        """Test hard deletion of an interaction."""
        # Configure mocks
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        mock_interaction = MagicMock()
        mock_interaction._id = ObjectId(interaction_id)
        mock_delete.return_value = mock_interaction

        # Make request with soft=false parameter
        response = self.client.delete(f'/api/interactions/{interaction_id}?soft=false', headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Interaction deleted successfully")
        
        # Verify mocks were called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_delete.assert_called_once_with(interaction_id, soft_delete=False)

    @patch('app.routes.interactions.is_admin')
    def test_delete_interaction_not_admin(self, mock_is_admin):
        """Test deletion of an interaction by a non-admin user."""
        # Configure mock
        mock_is_admin.return_value = False
        interaction_id = str(ObjectId())

        # Make request
        response = self.client.delete(f'/api/interactions/{interaction_id}', headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Admin privileges required")
        
        # Verify mock was called correctly
        mock_is_admin.assert_called_once_with(self.user_id)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_not_found(self, mock_delete, mock_is_admin):
        """Test deletion of a non-existent interaction."""
        # Configure mocks
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        mock_delete.return_value = None

        # Make request
        response = self.client.delete(f'/api/interactions/{interaction_id}', headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Interaction not found")
        
        # Verify mocks were called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_delete.assert_called_once_with(interaction_id, soft_delete=True)

    @patch('app.routes.interactions.is_admin')
    def test_delete_interaction_invalid_id(self, mock_is_admin):
        """Test deletion of an interaction with an invalid ID format."""
        # Configure mock
        mock_is_admin.return_value = True
        
        # Make request with invalid ID
        response = self.client.delete('/api/interactions/invalid-id', headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("not a valid ObjectId", data["error"])
        
        # Verify mock was called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_exception(self, mock_delete, mock_is_admin):
        """Test exception during interaction deletion."""
        # Configure mocks
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        mock_delete.side_effect = Exception("Database error")

        # Make request
        response = self.client.delete(f'/api/interactions/{interaction_id}', headers=self.admin_headers)
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Failed to delete interaction")
        self.assertEqual(data["details"], "Database error")
        
        # Verify mocks were called correctly
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_delete.assert_called_once_with(interaction_id, soft_delete=True)


if __name__ == '__main__':
    unittest.main() 