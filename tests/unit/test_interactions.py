import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from bson.objectid import ObjectId
from datetime import datetime, timezone
import uuid

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.interaction import Interaction
from app.models.user import User

class TestInteractions(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        # Create app for testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['JWT_ENABLED'] = False  # Disable JWT for testing
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Generate test IDs
        self.test_id = str(ObjectId())
        self.test_object_id = ObjectId(self.test_id)
        self.test_user_id = f"TEST_USER_{uuid.uuid4().hex[:8]}"
        self.test_supplement_id = f"SUPPLEMENT_{uuid.uuid4().hex[:8]}"
        
        # Sample interaction data with unique values
        timestamp = datetime.now(timezone.utc)
        self.test_interaction_data = {
            "_id": self.test_id,
            "interactionId": f"INTERACTION_{timestamp.timestamp()}",
            "interactionType": "supplement_supplement",
            "severity": "Medium",
            "effect": f"Test effect {uuid.uuid4().hex[:10]}",
            "description": f"Test description {uuid.uuid4().hex[:10]}",
            "recommendation": f"Test recommendation {uuid.uuid4().hex[:10]}",
            "supplements": [
                {"supplementId": self.test_supplement_id, "name": f"Supplement {uuid.uuid4().hex[:8]}"},
                {"supplementId": f"SUPPLEMENT_{uuid.uuid4().hex[:8]}", "name": f"Supplement {uuid.uuid4().hex[:8]}"}
            ],
            "foodItems": [],
            "medications": [],
            "references": [f"Reference {uuid.uuid4().hex[:8]}"],
            "createdAt": timestamp.isoformat(),
            "updatedAt": None,
            "isDeleted": False
        }
        
        # Mock interaction object
        self.mock_interaction = MagicMock()
        self.mock_interaction._id = self.test_id
        self.mock_interaction.interaction_id = self.test_interaction_data["interactionId"]
        self.mock_interaction.interaction_type = self.test_interaction_data["interactionType"]
        self.mock_interaction.severity = self.test_interaction_data["severity"]
        self.mock_interaction.effect = self.test_interaction_data["effect"]
        self.mock_interaction.description = self.test_interaction_data["description"]
        self.mock_interaction.recommendation = self.test_interaction_data["recommendation"]
        self.mock_interaction.supplements = self.test_interaction_data["supplements"]
        self.mock_interaction.food_items = self.test_interaction_data["foodItems"]
        self.mock_interaction.medications = self.test_interaction_data["medications"]
        self.mock_interaction.references = self.test_interaction_data["references"]
        self.mock_interaction.created_at = self.test_interaction_data["createdAt"]
        self.mock_interaction.updated_at = self.test_interaction_data["updatedAt"]
        self.mock_interaction.is_deleted = self.test_interaction_data["isDeleted"]
        self.mock_interaction.to_dict.return_value = self.test_interaction_data
        
        # Mock user for permission tests
        self.mock_user = MagicMock()
        self.mock_user.user_id = self.test_user_id
        self.mock_user.role = "user"
        
        # Mock admin user for admin tests
        self.mock_admin = MagicMock()
        self.mock_admin.user_id = f"ADMIN_{uuid.uuid4().hex[:8]}"
        self.mock_admin.role = "admin"
        
        # Set up JWT mocking
        self.jwt_patcher = patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
        self.get_jwt_identity_patcher = patch('app.routes.interactions.get_jwt_identity')
        self.find_user_patcher = patch('app.routes.interactions.User.find_by_id')
        
        # Start the patchers
        self.mock_verify_jwt = self.jwt_patcher.start()
        self.mock_jwt_identity = self.get_jwt_identity_patcher.start()
        self.mock_find_user = self.find_user_patcher.start()
        
        # Configure mocks
        self.mock_verify_jwt.return_value = None  # Skip JWT verification
        self.mock_jwt_identity.return_value = self.test_user_id
        self.mock_find_user.return_value = self.mock_admin  # User is admin by default for all tests
    
    def tearDown(self):
        """Tear down test fixtures after each test method is run."""
        # Stop the patchers
        self.jwt_patcher.stop()
        self.get_jwt_identity_patcher.stop()
        self.find_user_patcher.stop()
        self.app_context.pop()
    
    # GET /api/interactions/ - Get list of interactions
    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_no_filters(self, mock_find_all):
        """Test getting interactions without filters."""
        # Setup mock
        mock_find_all.return_value = [self.mock_interaction]
        
        # Make request
        response = self.client.get('/api/interactions/')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["interactionId"], self.test_interaction_data["interactionId"])
        
        # Verify mock was called with empty query
        mock_find_all.assert_called_once_with({})
    
    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_with_filters(self, mock_find_all):
        """Test getting interactions with type, severity, and search filters."""
        # Setup mock
        mock_find_all.return_value = [self.mock_interaction]
        
        # Make request with filters
        response = self.client.get(
            '/api/interactions/?type=supplement_supplement&severity=Medium&query=test'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        
        # Verify mock was called with correct filters
        expected_query = {
            'interactionType': 'supplement_supplement',
            'severity': 'Medium',
            '$or': [
                {'effect': {'$regex': 'test', '$options': 'i'}},
                {'description': {'$regex': 'test', '$options': 'i'}},
                {'recommendation': {'$regex': 'test', '$options': 'i'}}
            ]
        }
        mock_find_all.assert_called_once()
        actual_query = mock_find_all.call_args[0][0]
        self.assertEqual(actual_query.get('interactionType'), expected_query.get('interactionType'))
        self.assertEqual(actual_query.get('severity'), expected_query.get('severity'))
        self.assertIn('$or', actual_query)
    
    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_server_error(self, mock_find_all):
        """Test getting interactions with server error."""
        # Setup mock to raise an exception
        mock_find_all.side_effect = Exception("Database connection error")
        
        # Make request
        response = self.client.get('/api/interactions/')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to get interactions", data["error"])
    
    @patch('app.routes.interactions.Interaction.find_all')
    def test_get_interactions_value_error(self, mock_find_all):
        """Test getting interactions with value error."""
        # Setup mock to raise a ValueError
        mock_find_all.side_effect = ValueError("Invalid filter parameter")
        
        # Make request
        response = self.client.get('/api/interactions/')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Invalid filter parameter")
    
    # POST /api/interactions/ - Create a new interaction
    @patch('app.routes.interactions.Interaction.create')
    def test_create_interaction_success(self, mock_create):
        """Test creating a new interaction successfully."""
        # Setup mock
        mock_create.return_value = self.mock_interaction
        
        # Make request with data
        new_interaction = {
            "interactionType": "supplement_supplement",
            "severity": "High",
            "effect": "Decreased absorption",
            "description": "These supplements may interfere with each other",
            "recommendation": "Take at different times",
            "supplements": [
                {"supplementId": self.test_supplement_id, "name": "Calcium"},
                {"supplementId": f"SUPPLEMENT_{uuid.uuid4().hex[:8]}", "name": "Iron"}
            ]
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
        self.assertEqual(data["_id"], self.test_id)
        
        # Verify create was called with correct data
        mock_create.assert_called_once_with(new_interaction)
    
    def test_create_interaction_invalid_json(self):
        """Test creating an interaction with invalid JSON format."""
        # Make request with non-JSON data
        response = self.client.post(
            '/api/interactions/',
            data="This is not JSON",
            content_type='text/plain'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Missing JSON in request")
    
    @patch('app.routes.interactions.Interaction.create')
    def test_create_interaction_validation_error(self, mock_create):
        """Test creating an interaction with validation error."""
        # Setup mock to raise ValueError
        error_message = "Missing required field: severity"
        mock_create.side_effect = ValueError(error_message)
        
        # Make request with invalid data (missing severity)
        invalid_interaction = {
            "interactionType": "supplement_supplement",
            "effect": "Decreased absorption",
            "supplements": [
                {"supplementId": self.test_supplement_id}
            ]
        }
        
        response = self.client.post(
            '/api/interactions/',
            data=json.dumps(invalid_interaction),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], error_message)
    
    @patch('app.routes.interactions.Interaction.create')
    def test_create_interaction_server_error(self, mock_create):
        """Test creating an interaction with server error."""
        # Setup mock to raise an exception
        mock_create.side_effect = Exception("Database connection error")
        
        # Make request with data
        new_interaction = {
            "interactionType": "supplement_food",
            "severity": "Medium",
            "effect": "Decreased absorption",
            "supplements": [{"supplementId": self.test_supplement_id}],
            "foodItems": ["Grapefruit"]
        }
        
        response = self.client.post(
            '/api/interactions/',
            data=json.dumps(new_interaction),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to create interaction", data["error"])
    
    # GET /api/interactions/<interaction_id> - Get a specific interaction
    @patch('app.routes.interactions.Interaction.find_by_id')
    def test_get_interaction_by_id_success(self, mock_find_by_id):
        """Test getting a specific interaction by ID successfully."""
        # Setup mock
        mock_find_by_id.return_value = self.mock_interaction
        
        # Make request
        response = self.client.get(f'/api/interactions/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["interactionId"], self.test_interaction_data["interactionId"])
        self.assertEqual(data["severity"], self.test_interaction_data["severity"])
        
        # Verify mock was called with correct ID
        mock_find_by_id.assert_called_once_with(self.test_id)
    
    @patch('app.routes.interactions.Interaction.find_by_id')
    def test_get_interaction_by_id_not_found(self, mock_find_by_id):
        """Test getting a non-existent interaction by ID."""
        # Setup mock to return None
        mock_find_by_id.return_value = None
        
        # Make request
        response = self.client.get(f'/api/interactions/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Interaction not found")
        
        # Verify mock was called
        mock_find_by_id.assert_called_once()
    
    @patch('app.routes.interactions.Interaction.find_by_id')
    def test_get_interaction_server_error(self, mock_find_by_id):
        """Test getting a specific interaction with server error."""
        # Setup mock to raise an exception
        mock_find_by_id.side_effect = Exception("Database connection error")
        
        # Make request
        response = self.client.get(f'/api/interactions/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to get interaction", data["error"])
    
    # PUT /api/interactions/<interaction_id> - Update an interaction
    @patch('app.routes.interactions.Interaction.update')
    def test_update_interaction_success(self, mock_update):
        """Test updating an interaction successfully."""
        # Setup mock
        updated_interaction = MagicMock()
        updated_interaction._id = self.test_id
        mock_update.return_value = updated_interaction
        
        # Make request with update data
        update_data = {
            "severity": "Low",
            "recommendation": "Updated recommendation"
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
        
        # Verify update was called with correct data
        mock_update.assert_called_once_with(self.test_id, update_data)
    
    def test_update_interaction_invalid_json(self):
        """Test updating an interaction with invalid JSON format."""
        # Make request with non-JSON data
        response = self.client.put(
            f'/api/interactions/{self.test_id}',
            data="This is not JSON",
            content_type='text/plain'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Missing JSON in request")
    
    def test_update_interaction_empty_data(self):
        """Test updating an interaction with empty data."""
        # Make request with empty JSON
        response = self.client.put(
            f'/api/interactions/{self.test_id}',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "No update data provided")
    
    @patch('app.routes.interactions.Interaction.update')
    def test_update_interaction_validation_error(self, mock_update):
        """Test updating an interaction with validation error."""
        # Setup mock to raise ValueError
        error_message = "Invalid severity level"
        mock_update.side_effect = ValueError(error_message)
        
        # Make request with invalid data
        invalid_update = {
            "severity": "INVALID_LEVEL"
        }
        
        response = self.client.put(
            f'/api/interactions/{self.test_id}',
            data=json.dumps(invalid_update),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], error_message)
    
    @patch('app.routes.interactions.Interaction.update')
    def test_update_interaction_server_error(self, mock_update):
        """Test updating an interaction with server error."""
        # Setup mock to raise an exception
        mock_update.side_effect = Exception("Database connection error")
        
        # Make request with data
        update_data = {
            "severity": "High"
        }
        
        response = self.client.put(
            f'/api/interactions/{self.test_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to update interaction", data["error"])
    
    # DELETE /api/interactions/<interaction_id> - Delete an interaction
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_success_soft(self, mock_delete):
        """Test soft deleting an interaction successfully."""
        # Setup mock
        deleted_interaction = MagicMock()
        deleted_interaction._id = self.test_id
        mock_delete.return_value = deleted_interaction
        
        # Make request for soft delete (default)
        response = self.client.delete(f'/api/interactions/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Interaction deleted successfully")
        
        # Verify mock was called with correct parameters
        mock_delete.assert_called_once_with(self.test_id, soft_delete=True)
    
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_success_hard(self, mock_delete):
        """Test hard deleting an interaction successfully."""
        # Setup mock
        deleted_interaction = MagicMock()
        deleted_interaction._id = self.test_id
        mock_delete.return_value = deleted_interaction
        
        # Make request for hard delete
        response = self.client.delete(f'/api/interactions/{self.test_id}?soft=false')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Interaction deleted successfully")
        
        # Verify mock was called with correct parameters
        mock_delete.assert_called_once_with(self.test_id, soft_delete=False)
    
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_not_found(self, mock_delete):
        """Test deleting a non-existent interaction."""
        # Setup mock to return None
        mock_delete.return_value = None
        
        # Make request
        response = self.client.delete(f'/api/interactions/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Interaction not found")
    
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_value_error(self, mock_delete):
        """Test deleting an interaction with validation error."""
        # Setup mock to raise ValueError
        error_message = "Cannot delete referenced interaction"
        mock_delete.side_effect = ValueError(error_message)
        
        # Make request
        response = self.client.delete(f'/api/interactions/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], error_message)
    
    @patch('app.routes.interactions.Interaction.delete')
    def test_delete_interaction_server_error(self, mock_delete):
        """Test deleting an interaction with server error."""
        # Setup mock to raise an exception
        mock_delete.side_effect = Exception("Database connection error")
        
        # Make request
        response = self.client.delete(f'/api/interactions/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to delete interaction", data["error"])
    
    # POST /api/interactions/check - Check for interactions
    @patch('app.routes.interactions.Interaction.check_interactions')
    def test_check_interactions_success(self, mock_check_interactions):
        """Test checking for interactions successfully."""
        # Setup mock to return interactions
        mock_check_interactions.return_value = [self.mock_interaction]
        
        # Make request with data
        check_data = {
            "supplementIds": [self.test_supplement_id],
            "foodItems": ["Grapefruit"],
            "medications": ["Warfarin"]
        }
        
        response = self.client.post(
            '/api/interactions/check',
            data=json.dumps(check_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 1)
        self.assertEqual(len(data["interactions"]), 1)
        
        # Verify mock was called with correct parameters
        mock_check_interactions.assert_called_once_with(
            supplement_ids=[self.test_supplement_id],
            food_items=["Grapefruit"],
            medications=["Warfarin"]
        )
    
    def test_check_interactions_invalid_json(self):
        """Test checking interactions with invalid JSON format."""
        # Make request with non-JSON data
        response = self.client.post(
            '/api/interactions/check',
            data="This is not JSON",
            content_type='text/plain'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Missing JSON in request")
    
    def test_check_interactions_missing_supplements(self):
        """Test checking interactions without providing supplement IDs."""
        # Make request without supplement IDs
        request_data = {
            "foodItems": ["Grapefruit"],
            "medications": ["Warfarin"]
        }
        
        response = self.client.post(
            '/api/interactions/check',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "At least one supplement ID is required")
    
    @patch('app.routes.interactions.Interaction.check_interactions')
    def test_check_interactions_value_error(self, mock_check_interactions):
        """Test checking interactions with validation error."""
        # Setup mock to raise ValueError
        error_message = "Invalid supplement ID format"
        mock_check_interactions.side_effect = ValueError(error_message)
        
        # Make request with invalid data
        request_data = {
            "supplementIds": ["INVALID_ID_FORMAT"]
        }
        
        response = self.client.post(
            '/api/interactions/check',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], error_message)
    
    @patch('app.routes.interactions.Interaction.check_interactions')
    def test_check_interactions_server_error(self, mock_check_interactions):
        """Test checking interactions with server error."""
        # Setup mock to raise an exception
        mock_check_interactions.side_effect = Exception("Database connection error")
        
        # Make request with data
        request_data = {
            "supplementIds": [self.test_supplement_id]
        }
        
        response = self.client.post(
            '/api/interactions/check',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to check interactions", data["error"])


if __name__ == '__main__':
    unittest.main()
