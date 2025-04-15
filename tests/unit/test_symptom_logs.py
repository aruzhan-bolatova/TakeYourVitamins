import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from bson.objectid import ObjectId
from datetime import datetime, timezone, timedelta
import uuid

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.symptom_log import SymptomLog
from app.models.user import User

class TestSymptomLogs(unittest.TestCase):
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
        
        # Sample symptom log data with unique values
        timestamp = datetime.now(timezone.utc)
        self.test_log_data = {
            "_id": self.test_id,
            "symptomLogId": f"SYMPTOM_{timestamp.timestamp()}",
            "userId": self.test_user_id,
            "symptom": f"Headache_{uuid.uuid4().hex[:6]}",
            "rating": 7,
            "logDate": timestamp.isoformat(),
            "comments": f"Test symptoms {uuid.uuid4().hex[:10]}",
            "intakeLogId": f"INTAKE_{uuid.uuid4().hex[:8]}",
            "createdAt": timestamp.isoformat(),
            "updatedAt": None,
            "isDeleted": False
        }
        
        # Mock symptom log object
        self.mock_log = MagicMock()
        self.mock_log._id = self.test_id
        self.mock_log.symptom_log_id = self.test_log_data["symptomLogId"]
        self.mock_log.user_id = self.test_log_data["userId"]
        self.mock_log.symptom = self.test_log_data["symptom"]
        self.mock_log.rating = self.test_log_data["rating"]
        self.mock_log.log_date = self.test_log_data["logDate"]
        self.mock_log.comments = self.test_log_data["comments"]
        self.mock_log.intake_log_id = self.test_log_data["intakeLogId"]
        self.mock_log.created_at = self.test_log_data["createdAt"]
        self.mock_log.updated_at = self.test_log_data["updatedAt"]
        self.mock_log.is_deleted = self.test_log_data["isDeleted"]
        self.mock_log.to_dict.return_value = self.test_log_data
        
        # Mock user for permission tests
        self.mock_user = MagicMock()
        self.mock_user.user_id = self.test_user_id
        self.mock_user.role = "user"
        
        # Mock admin user for admin tests
        self.mock_admin = MagicMock()
        self.mock_admin.user_id = f"ADMIN_{uuid.uuid4().hex[:8]}"
        self.mock_admin.role = "admin"
        
        # Set up JWT mocking - using a better approach
        self.jwt_patcher = patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
        self.get_jwt_identity_patcher = patch('app.routes.symptom_logs.get_jwt_identity')
        
        # Start the patchers
        self.mock_verify_jwt = self.jwt_patcher.start()
        self.mock_jwt_identity = self.get_jwt_identity_patcher.start()
        
        # Configure mocks
        self.mock_verify_jwt.return_value = None  # Skip JWT verification
        self.mock_jwt_identity.return_value = self.test_user_id
    
    def tearDown(self):
        """Tear down test fixtures after each test method is run."""
        # Stop the patchers
        self.jwt_patcher.stop()
        self.get_jwt_identity_patcher.stop()
        self.app_context.pop()
    
    # GET /api/symptom-logs/ - Get list of symptom logs
    @patch('app.models.symptom_log.SymptomLog.search')
    def test_get_symptom_logs_for_current_user(self, mock_search):
        """Test getting symptom logs for the current user (from JWT token)."""
        # Setup mock to return a list of logs
        mock_search.return_value = [self.mock_log]
        
        # Make request
        response = self.client.get('/api/symptom-logs/')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["symptomLogId"], self.test_log_data["symptomLogId"])
        self.assertEqual(data[0]["symptom"], self.test_log_data["symptom"])
        
        # Verify mock was called with user from JWT token and empty date filters
        mock_search.assert_called_once_with(user_id=self.test_user_id, date_from='', date_to='')
    
    @patch('app.models.symptom_log.SymptomLog.search')
    @patch('app.models.user.User.find_by_id')
    def test_get_all_symptom_logs_as_admin(self, mock_find_user, mock_search):
        """Test getting all symptom logs as admin."""
        # Setup mocks
        mock_find_user.return_value = self.mock_admin
        mock_search.return_value = [self.mock_log]
        
        # Make request to the admin endpoint
        response = self.client.get('/api/symptom-logs/all')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        
        # Verify mocks were called correctly
        mock_find_user.assert_called_once_with(self.test_user_id)
        mock_search.assert_called_once_with(user_id='', date_from='', date_to='')
    
    @patch('app.models.user.User.find_by_id')
    def test_get_all_symptom_logs_as_non_admin(self, mock_find_user):
        """Test that non-admin users cannot access all logs."""
        # Setup mock to return a regular user
        mock_find_user.return_value = self.mock_user
        
        # Make request to the admin endpoint
        response = self.client.get('/api/symptom-logs/all')
        
        # Assert response shows access denied
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("permission", data["error"].lower())
        
        # Verify user was checked
        mock_find_user.assert_called_once_with(self.test_user_id)
    
    # GET /api/symptom-logs/<log_id> - Get a specific symptom log
    @patch('app.models.symptom_log.SymptomLog.find_by_id')
    def test_get_symptom_log_by_id_success(self, mock_find_by_id):
        """Test getting a specific symptom log by ID successfully."""
        # Setup mock to return a log owned by the current user
        mock_find_by_id.return_value = self.mock_log
        
        # Make request
        response = self.client.get(f'/api/symptom-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["symptomLogId"], self.test_log_data["symptomLogId"])
        self.assertEqual(data["symptom"], self.test_log_data["symptom"])
        
        # Verify mock was called with correct ID
        mock_find_by_id.assert_called_once_with(self.test_object_id)
    
    @patch('app.models.symptom_log.SymptomLog.find_by_id')
    @patch('app.models.user.User.find_by_id')
    def test_get_symptom_log_permission_denied(self, mock_find_user, mock_find_log):
        """Test that a user cannot access another user's log."""
        # Setup mocks for a different user
        different_user_log = MagicMock()
        different_user_log.user_id = f"OTHER_USER_{uuid.uuid4().hex[:8]}"
        mock_find_log.return_value = different_user_log
        mock_find_user.return_value = self.mock_user  # Regular user, not admin
        
        # Make request
        response = self.client.get(f'/api/symptom-logs/{self.test_id}')
        
        # Assert response shows permission denied
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("permission", data["error"].lower())
        
        # Verify mocks were called
        mock_find_log.assert_called_once_with(self.test_object_id)
        mock_find_user.assert_called_once_with(self.test_user_id)
    
    @patch('app.models.symptom_log.SymptomLog.find_by_id')
    def test_get_symptom_log_by_id_not_found(self, mock_find_by_id):
        """Test getting a non-existent symptom log by ID."""
        # Setup mock to return None
        mock_find_by_id.return_value = None
        
        # Make request
        response = self.client.get(f'/api/symptom-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Symptom log not found")
        
        # Verify mock was called
        mock_find_by_id.assert_called_once()
    
    # POST /api/symptom-logs/ - Create a new symptom log
    @patch('app.routes.symptom_logs.get_db')
    def test_create_symptom_log_success(self, mock_get_db):
        """Test creating a new symptom log successfully."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.SymptomLogs = mock_collection
        mock_get_db.return_value = mock_db
        
        # Setup insert_one mock
        mock_result = MagicMock()
        mock_result.inserted_id = self.test_object_id
        mock_collection.insert_one.return_value = mock_result

        # Make request with data
        new_log = {
            "symptom": f"Nausea_{uuid.uuid4().hex[:6]}",
            "rating": 6,
            "logDate": datetime.now(timezone.utc).isoformat(),
            "comments": f"After taking vitamin B {uuid.uuid4().hex[:8]}"
        }
        
        response = self.client.post(
            '/api/symptom-logs/',
            data=json.dumps(new_log),
            content_type='application/json'
        )
        
        # Assert response status and data
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["message"], "Symptom log created successfully")
        self.assertIn("_id", data)
        
        # Verify the mock DB was used
        mock_collection.insert_one.assert_called_once()
    
    # PUT /api/symptom-logs/<log_id> - Update a symptom log
    @patch('app.models.symptom_log.SymptomLog.find_by_id')
    @patch('app.models.symptom_log.SymptomLog.update')
    def test_update_symptom_log_success(self, mock_update, mock_find_by_id):
        """Test updating a symptom log successfully."""
        # Setup mocks
        mock_find_by_id.return_value = self.mock_log  # Log owned by current user
        mock_update.return_value = True
        
        # Make request
        update_data = {
            "rating": 8,
            "comments": f"Updated comments about headache {uuid.uuid4().hex[:8]}"
        }
        
        response = self.client.put(
            f'/api/symptom-logs/{self.test_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Symptom log updated successfully")
        
        # Verify mocks were called with correct parameters
        mock_find_by_id.assert_called_once_with(self.test_object_id)
        mock_update.assert_called_once_with(self.test_object_id, update_data)
    
    @patch('app.models.symptom_log.SymptomLog.find_by_id')
    @patch('app.models.user.User.find_by_id')
    def test_update_symptom_log_permission_denied(self, mock_find_user, mock_find_log):
        """Test that a user cannot update another user's log."""
        # Setup mocks for a different user
        different_user_log = MagicMock()
        different_user_log.user_id = f"OTHER_USER_{uuid.uuid4().hex[:8]}"
        mock_find_log.return_value = different_user_log
        mock_find_user.return_value = self.mock_user  # Regular user, not admin
        
        # Make request
        update_data = {
            "rating": 8
        }
        
        response = self.client.put(
            f'/api/symptom-logs/{self.test_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert response shows permission denied
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("permission", data["error"].lower())
    
    # DELETE /api/symptom-logs/<log_id> - Delete a symptom log
    @patch('app.models.symptom_log.SymptomLog.find_by_id')
    @patch('app.models.symptom_log.SymptomLog.delete')
    def test_delete_symptom_log_success_soft(self, mock_delete, mock_find_by_id):
        """Test soft deleting a symptom log successfully."""
        # Setup mocks
        mock_find_by_id.return_value = self.mock_log  # Log owned by current user
        mock_delete.return_value = True
        
        # Make request for soft delete (default)
        response = self.client.delete(f'/api/symptom-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Symptom log deleted successfully")
        
        # Verify mocks were called with correct parameters
        mock_find_by_id.assert_called_once_with(self.test_object_id)
        mock_delete.assert_called_with(self.test_object_id, soft_delete=True)
    
    @patch('app.models.symptom_log.SymptomLog.find_by_id')
    @patch('app.models.user.User.find_by_id')
    @patch('app.models.symptom_log.SymptomLog.delete')
    def test_delete_symptom_log_as_admin(self, mock_delete, mock_find_user, mock_find_log):
        """Test that an admin can delete any symptom log."""
        # Setup mocks
        different_user_log = MagicMock()
        different_user_log.user_id = f"OTHER_USER_{uuid.uuid4().hex[:8]}"
        mock_find_log.return_value = different_user_log
        mock_find_user.return_value = self.mock_admin  # Admin user
        mock_delete.return_value = True
        
        # Make request
        response = self.client.delete(f'/api/symptom-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Symptom log deleted successfully")
        
        # Verify admin check was performed and delete was called
        mock_find_user.assert_called_once()
        mock_delete.assert_called_once()


if __name__ == '__main__':
    unittest.main()
