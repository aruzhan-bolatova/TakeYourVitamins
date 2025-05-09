import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from flask_jwt_extended import create_access_token, JWTManager
from bson.objectid import ObjectId
import sys
import os

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.interaction import Interaction
from app.models.user import User
from app.routes.interactions import bp as interactions_bp  # Import the blueprint

# Mock the interactions module if needed, though likely not needed here directly
# sys.modules['interactions'] = MagicMock()

class TestInteractionsRoutes(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'  # Use a test secret key
        self.client = self.app.test_client()
        self.jwt = JWTManager(self.app)

        # Push application context so create_access_token works
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create a dummy user for context if needed
        self.user_id = str(ObjectId())
        self.admin_user_id = str(ObjectId())
        self.access_token = create_access_token(identity=self.user_id)
        self.admin_access_token = create_access_token(identity=self.admin_user_id)
        self.headers = {'Authorization': f'Bearer {self.access_token}'}
        self.admin_headers = {'Authorization': f'Bearer {self.admin_access_token}'}

        # Register the blueprint *after* JWTManager is initialized
        self.app.register_blueprint(interactions_bp)

    def tearDown(self):
        # Pop application context after test
        self.app_context.pop()

    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_success(self, mock_find_all):
        """Test successful retrieval of interactions."""
        # Mock Interaction.find_all to return some mock interactions
        mock_interaction1 = MagicMock(spec=Interaction)
        mock_interaction1.to_dict.return_value = {'_id': 'int1', 'interactionType': 'Drug-Supplement', 'effect': 'Reduced absorption'}
        mock_interaction2 = MagicMock(spec=Interaction)
        mock_interaction2.to_dict.return_value = {'_id': 'int2', 'interactionType': 'Food-Supplement', 'effect': 'Increased potency'}
        mock_find_all.return_value = [mock_interaction1, mock_interaction2]

        response = self.client.get('/api/interactions/', headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['_id'], 'int1')
        self.assertEqual(data[1]['effect'], 'Increased potency')
        mock_find_all.assert_called_once_with({}) # No query parameters

    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_with_type_filter(self, mock_find_all):
        """Test retrieving interactions filtered by type."""
        mock_interaction1 = MagicMock(spec=Interaction)
        mock_interaction1.to_dict.return_value = {'_id': 'int1', 'interactionType': 'Drug-Supplement', 'effect': 'Reduced absorption'}
        mock_find_all.return_value = [mock_interaction1]

        response = self.client.get('/api/interactions/?type=Drug-Supplement', headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['interactionType'], 'Drug-Supplement')
        mock_find_all.assert_called_once_with({'interactionType': 'Drug-Supplement'})

    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_with_search_query(self, mock_find_all):
        """Test retrieving interactions with a search query."""
        mock_interaction1 = MagicMock(spec=Interaction)
        mock_interaction1.to_dict.return_value = {'_id': 'int1', 'description': 'This causes reduced absorption'}
        mock_find_all.return_value = [mock_interaction1]
        search_term = 'absorption'

        response = self.client.get(f'/api/interactions/?query={search_term}', headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertIn(search_term, data[0]['description'])
        expected_query = {
            '$or': [
                {'effect': {'$regex': search_term, '$options': 'i'}},
                {'description': {'$regex': search_term, '$options': 'i'}},
                {'recommendation': {'$regex': search_term, '$options': 'i'}}
            ]
        }
        mock_find_all.assert_called_once_with(expected_query)

    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_value_error(self, mock_find_all):
        """Test ValueError during interaction retrieval."""
        mock_find_all.side_effect = ValueError("Invalid query parameter")

        response = self.client.get('/api/interactions/?type=InvalidType', headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Invalid query parameter")

    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_exception(self, mock_find_all):
        """Test general exception during interaction retrieval."""
        mock_find_all.side_effect = Exception("Database connection failed")

        response = self.client.get('/api/interactions/', headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 500)
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Failed to get interactions")
        self.assertIn('details', data)
        self.assertEqual(data['details'], "Database connection failed")

    # --- Tests for POST /api/interactions/ ---

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.create')
    def test_create_interaction_success_admin(self, mock_create, mock_is_admin):
        """Test successful creation of an interaction by an admin."""
        mock_is_admin.return_value = True
        interaction_data = {'interactionType': 'TestType', 'effect': 'TestEffect'}
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction._id = ObjectId()
        mock_create.return_value = mock_interaction

        response = self.client.post('/api/interactions/', json=interaction_data, headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], "Interaction created successfully")
        self.assertEqual(data['_id'], str(mock_interaction._id))
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_create.assert_called_once_with(interaction_data)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.create')
    def test_create_interaction_forbidden_non_admin(self, mock_create, mock_is_admin):
        """Test that non-admin users cannot create interactions."""
        mock_is_admin.return_value = False
        interaction_data = {'interactionType': 'TestType', 'effect': 'TestEffect'}

        response = self.client.post('/api/interactions/', json=interaction_data, headers=self.headers) # Using non-admin token
        data = response.get_json()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['error'], "Admin privileges required")
        mock_is_admin.assert_called_once_with(self.user_id)
        mock_create.assert_not_called()

    @patch('app.routes.interactions.is_admin')
    def test_create_interaction_missing_json(self, mock_is_admin):
        """Test creating an interaction with missing JSON payload."""
        mock_is_admin.return_value = True

        response = self.client.post('/api/interactions/', headers=self.admin_headers) # No json data
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "Missing JSON in request")
        mock_is_admin.assert_called_once_with(self.admin_user_id)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.create')
    def test_create_interaction_value_error(self, mock_create, mock_is_admin):
        """Test ValueError during interaction creation (e.g., invalid data)."""
        mock_is_admin.return_value = True
        interaction_data = {'invalid_field': 'value'} # Missing required fields
        mock_create.side_effect = ValueError("Missing required field: interactionType")

        response = self.client.post('/api/interactions/', json=interaction_data, headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "Missing required field: interactionType")
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_create.assert_called_once_with(interaction_data)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.create')
    def test_create_interaction_exception(self, mock_create, mock_is_admin):
        """Test general exception during interaction creation."""
        mock_is_admin.return_value = True
        interaction_data = {'interactionType': 'TestType', 'effect': 'TestEffect'}
        mock_create.side_effect = Exception("Database error")

        response = self.client.post('/api/interactions/', json=interaction_data, headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['error'], "Failed to create interaction")
        self.assertIn('details', data)
        self.assertEqual(data['details'], "Database error")
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_create.assert_called_once_with(interaction_data)

    # --- Tests for GET /api/interactions/<interaction_id> ---

    @patch('app.routes.interactions.Interaction.find_by_id')
    def test_get_interaction_by_id_success(self, mock_find_by_id):
        """Test successful retrieval of a specific interaction by ID."""
        interaction_id = str(ObjectId())
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.to_dict.return_value = {'_id': interaction_id, 'interactionType': 'Test', 'effect': 'Found'}
        mock_find_by_id.return_value = mock_interaction

        response = self.client.get(f'/api/interactions/{interaction_id}', headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['_id'], interaction_id)
        self.assertEqual(data['effect'], 'Found')
        mock_find_by_id.assert_called_once_with(interaction_id)

    @patch('app.routes.interactions.Interaction.find_by_id')
    def test_get_interaction_by_id_not_found(self, mock_find_by_id):
        """Test retrieving an interaction that does not exist."""
        interaction_id = str(ObjectId())
        mock_find_by_id.return_value = None

        response = self.client.get(f'/api/interactions/{interaction_id}', headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Interaction not found")
        mock_find_by_id.assert_called_once_with(interaction_id)

    @patch('app.routes.interactions.Interaction.find_by_id')
    def test_get_interaction_by_id_value_error(self, mock_find_by_id):
        """Test retrieving an interaction with an invalid ID format (causes ValueError)."""
        invalid_id = "not-an-objectid"
        # Mocking find_by_id to raise ValueError, simulating BSON ObjectId error
        mock_find_by_id.side_effect = ValueError("Invalid ObjectId")

        response = self.client.get(f'/api/interactions/{invalid_id}', headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "Invalid ObjectId")
        # Check it was called with the invalid ID before raising the error
        mock_find_by_id.assert_called_once_with(invalid_id)

    @patch('app.routes.interactions.Interaction.find_by_id')
    def test_get_interaction_by_id_exception(self, mock_find_by_id):
        """Test general exception during specific interaction retrieval."""
        interaction_id = str(ObjectId())
        mock_find_by_id.side_effect = Exception("Server blew up")

        response = self.client.get(f'/api/interactions/{interaction_id}', headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['error'], "Failed to get interaction")
        self.assertIn('details', data)
        self.assertEqual(data['details'], "Server blew up")
        mock_find_by_id.assert_called_once_with(interaction_id)

    # --- Tests for PUT /api/interactions/<interaction_id> ---

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.update')
    def test_update_interaction_success_admin(self, mock_update, mock_is_admin):
        """Test successful update of an interaction by an admin."""
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        update_data = {'effect': 'Updated Effect'}
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction._id = ObjectId(interaction_id) # Simulate update returning the object
        mock_update.return_value = mock_interaction

        response = self.client.put(f'/api/interactions/{interaction_id}', json=update_data, headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Interaction updated successfully")
        self.assertEqual(data['_id'], interaction_id)
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_update.assert_called_once_with(interaction_id, update_data)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.update')
    def test_update_interaction_forbidden_non_admin(self, mock_update, mock_is_admin):
        """Test that non-admin users cannot update interactions."""
        mock_is_admin.return_value = False
        interaction_id = str(ObjectId())
        update_data = {'effect': 'Updated Effect'}

        response = self.client.put(f'/api/interactions/{interaction_id}', json=update_data, headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['error'], "Admin privileges required")
        mock_is_admin.assert_called_once_with(self.user_id)
        mock_update.assert_not_called()

    @patch('app.routes.interactions.is_admin')
    def test_update_interaction_missing_json(self, mock_is_admin):
        """Test updating an interaction with missing JSON payload."""
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())

        response = self.client.put(f'/api/interactions/{interaction_id}', headers=self.admin_headers) # No json data
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "Missing JSON in request")
        mock_is_admin.assert_called_once_with(self.admin_user_id)

    @patch('app.routes.interactions.is_admin')
    def test_update_interaction_empty_data(self, mock_is_admin):
        """Test updating an interaction with empty JSON data."""
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())

        response = self.client.put(f'/api/interactions/{interaction_id}', json={}, headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "No update data provided")
        mock_is_admin.assert_called_once_with(self.admin_user_id)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.update')
    def test_update_interaction_value_error(self, mock_update, mock_is_admin):
        """Test ValueError during interaction update (e.g., invalid ID or data)."""
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        update_data = {'effect': 'New Effect'}
        mock_update.side_effect = ValueError("Interaction not found or invalid data")

        response = self.client.put(f'/api/interactions/{interaction_id}', json=update_data, headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "Interaction not found or invalid data")
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_update.assert_called_once_with(interaction_id, update_data)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.update')
    def test_update_interaction_exception(self, mock_update, mock_is_admin):
        """Test general exception during interaction update."""
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        update_data = {'effect': 'New Effect'}
        mock_update.side_effect = Exception("Something went wrong")

        response = self.client.put(f'/api/interactions/{interaction_id}', json=update_data, headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['error'], "Failed to update interaction")
        self.assertIn('details', data)
        self.assertEqual(data['details'], "Something went wrong")
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_update.assert_called_once_with(interaction_id, update_data)

    # --- Tests for DELETE /api/interactions/<interaction_id> ---

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_success_admin_soft(self, mock_delete, mock_is_admin):
        """Test successful soft deletion of an interaction by an admin (default)."""
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction._id = ObjectId(interaction_id)
        mock_delete.return_value = mock_interaction

        response = self.client.delete(f'/api/interactions/{interaction_id}', headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Interaction deleted successfully")
        self.assertEqual(data['_id'], interaction_id)
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        # Default is soft delete
        mock_delete.assert_called_once_with(interaction_id, soft_delete=True)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_success_admin_hard(self, mock_delete, mock_is_admin):
        """Test successful hard deletion of an interaction by an admin."""
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction._id = ObjectId(interaction_id)
        mock_delete.return_value = mock_interaction

        response = self.client.delete(f'/api/interactions/{interaction_id}?soft=false', headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Interaction deleted successfully")
        self.assertEqual(data['_id'], interaction_id)
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_delete.assert_called_once_with(interaction_id, soft_delete=False)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_forbidden_non_admin(self, mock_delete, mock_is_admin):
        """Test that non-admin users cannot delete interactions."""
        mock_is_admin.return_value = False
        interaction_id = str(ObjectId())

        response = self.client.delete(f'/api/interactions/{interaction_id}', headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['error'], "Admin privileges required")
        mock_is_admin.assert_called_once_with(self.user_id)
        mock_delete.assert_not_called()

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_not_found(self, mock_delete, mock_is_admin):
        """Test deleting an interaction that does not exist."""
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        mock_delete.return_value = None # Simulate interaction not found

        response = self.client.delete(f'/api/interactions/{interaction_id}', headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Interaction not found")
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_delete.assert_called_once_with(interaction_id, soft_delete=True)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_value_error(self, mock_delete, mock_is_admin):
        """Test ValueError during interaction deletion (e.g., invalid ID format)."""
        mock_is_admin.return_value = True
        invalid_id = "invalid-id"
        mock_delete.side_effect = ValueError("Invalid ObjectId format")

        response = self.client.delete(f'/api/interactions/{invalid_id}', headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "Invalid ObjectId format")
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_delete.assert_called_once_with(invalid_id, soft_delete=True)

    @patch('app.routes.interactions.is_admin')
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_exception(self, mock_delete, mock_is_admin):
        """Test general exception during interaction deletion."""
        mock_is_admin.return_value = True
        interaction_id = str(ObjectId())
        mock_delete.side_effect = Exception("DB went boom")

        response = self.client.delete(f'/api/interactions/{interaction_id}', headers=self.admin_headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['error'], "Failed to delete interaction")
        self.assertIn('details', data)
        self.assertEqual(data['details'], "DB went boom")
        mock_is_admin.assert_called_once_with(self.admin_user_id)
        mock_delete.assert_called_once_with(interaction_id, soft_delete=True)


if __name__ == '__main__':
    unittest.main()
