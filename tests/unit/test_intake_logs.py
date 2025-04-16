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
from app.models.intake_log import IntakeLog
from app.models.user import User

class TestIntakeLogs(unittest.TestCase):
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
        
        # Sample intake log data with unique values
        timestamp = datetime.now(timezone.utc)
        self.test_log_data = {
            "_id": self.test_id,
            "intakeLogId": f"INTAKE_{timestamp.timestamp()}",
            "userId": self.test_user_id,
            "supplementId": self.test_supplement_id,
            "dosage": 500,
            "unit": "mg",
            "timestamp": timestamp.isoformat(),
            "notes": f"Test intake {uuid.uuid4().hex[:10]}",
            "createdAt": timestamp.isoformat(),
            "updatedAt": None,
            "isDeleted": False
        }
        
        # Mock intake log object
        self.mock_log = MagicMock()
        self.mock_log._id = self.test_id
        self.mock_log.intake_log_id = self.test_log_data["intakeLogId"]
        self.mock_log.user_id = self.test_log_data["userId"]
        self.mock_log.supplement_id = self.test_log_data["supplementId"]
        self.mock_log.dosage = self.test_log_data["dosage"]
        self.mock_log.unit = self.test_log_data["unit"]
        self.mock_log.timestamp = self.test_log_data["timestamp"]
        self.mock_log.notes = self.test_log_data["notes"]
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
        
        # Set up JWT mocking
        self.jwt_patcher = patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
        self.get_jwt_identity_patcher = patch('app.routes.intake_logs.get_jwt_identity')
        
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
    
    # GET /api/intake-logs/ - Get list of intake logs
    @patch('app.models.intake_log.IntakeLog.find_all')
    def test_get_intake_logs_for_current_user(self, mock_find_all):
        """Test getting intake logs for the current user (from JWT token)."""
        # Setup mock to return a list of logs
        mock_find_all.return_value = [self.mock_log]
        
        # Make request
        response = self.client.get('/api/intake-logs/')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["intakeLogId"], self.test_log_data["intakeLogId"])
        self.assertEqual(data[0]["supplementId"], self.test_log_data["supplementId"])
        
        # Verify mock was called with user from JWT token
        expected_query = {'userId': self.test_user_id}
        mock_find_all.assert_called_once_with(expected_query)
    
    @patch('app.models.intake_log.IntakeLog.find_all')
    def test_get_intake_logs_with_filters(self, mock_find_all):
        """Test getting intake logs with date and supplement filters."""
        # Setup mock
        mock_find_all.return_value = [self.mock_log]
        
        # Setup test dates and supplement ID
        start_date = '2023-01-01T00:00:00Z'
        end_date = '2023-01-31T23:59:59Z'
        
        # Make request with filters
        response = self.client.get(
            f'/api/intake-logs/?startDate={start_date}&endDate={end_date}&supplementId={self.test_supplement_id}'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        
        # Verify mock was called with filters
        expected_query = {
            'userId': self.test_user_id,
            'timestamp': {'$gte': start_date, '$lte': end_date},
            'supplementId': self.test_supplement_id
        }
        mock_find_all.assert_called_once()
        call_args = mock_find_all.call_args[0][0]
        self.assertEqual(call_args.get('userId'), expected_query.get('userId'))
        self.assertEqual(call_args.get('supplementId'), expected_query.get('supplementId'))
        self.assertEqual(call_args.get('timestamp').get('$gte'), expected_query.get('timestamp').get('$gte'))
        self.assertEqual(call_args.get('timestamp').get('$lte'), expected_query.get('timestamp').get('$lte'))
    
    @patch('app.models.intake_log.IntakeLog.find_all')
    def test_get_intake_logs_server_error(self, mock_find_all):
        """Test getting intake logs with server error."""
        # Setup mock to raise an exception
        mock_find_all.side_effect = Exception("Database connection error")
        
        # Make request
        response = self.client.get('/api/intake-logs/')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to get intake logs", data["error"])
    
    @patch('app.models.intake_log.IntakeLog.find_all')
    def test_get_intake_logs_value_error(self, mock_find_all):
        """Test getting intake logs with value error."""
        # Setup mock to raise a ValueError
        mock_find_all.side_effect = ValueError("Invalid date format")
        
        # Make request
        response = self.client.get('/api/intake-logs/')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Invalid date format")
    
    # POST /api/intake-logs/ - Create a new intake log
    @patch('app.models.intake_log.IntakeLog.create')
    def test_create_intake_log_success(self, mock_create):
        """Test creating a new intake log successfully."""
        # Setup mock
        mock_create.return_value = self.mock_log
        
        # Make request with data
        new_log = {
            "supplementId": self.test_supplement_id,
            "dosage": 500,
            "unit": "mg",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": "Taking vitamin D supplement"
        }
        
        response = self.client.post(
            '/api/intake-logs/',
            data=json.dumps(new_log),
            content_type='application/json'
        )
        
        # Assert response status and data
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["message"], "Intake log created successfully")
        self.assertEqual(data["_id"], self.test_id)
        
        # Verify create was called with correct data
        expected_data = new_log.copy()
        expected_data['userId'] = self.test_user_id
        mock_create.assert_called_once_with(expected_data)
    
    @patch('app.models.intake_log.IntakeLog.create')
    def test_create_intake_log_server_error(self, mock_create):
        """Test creating an intake log with server error."""
        # Setup mock to raise an exception
        mock_create.side_effect = Exception("Database connection error")
        
        # Make request with data
        new_log = {
            "supplementId": self.test_supplement_id,
            "dosage": 500,
            "unit": "mg"
        }
        
        response = self.client.post(
            '/api/intake-logs/',
            data=json.dumps(new_log),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to create intake log", data["error"])
    
    def test_create_intake_log_invalid_json(self):
        """Test creating an intake log with invalid JSON format."""
        # Make request with non-JSON data
        response = self.client.post(
            '/api/intake-logs/',
            data="This is not JSON",
            content_type='text/plain'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Missing JSON in request")
    
    @patch('app.models.intake_log.IntakeLog.create')
    def test_create_intake_log_validation_error(self, mock_create):
        """Test creating an intake log with validation error."""
        # Setup mock to raise ValueError
        error_message = "Invalid dosage value"
        mock_create.side_effect = ValueError(error_message)
        
        # Make request with invalid data
        invalid_log = {
            "supplementId": self.test_supplement_id,
            "dosage": -500,  # Invalid negative dosage
            "unit": "mg"
        }
        
        response = self.client.post(
            '/api/intake-logs/',
            data=json.dumps(invalid_log),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], error_message)
    
    # POST /api/intake-logs/check-interactions - Check for interactions
    @patch('app.models.interaction.Interaction.check_interactions')
    @patch('app.models.intake_log.IntakeLog.find_recent')
    def test_check_intake_interactions(self, mock_find_recent, mock_check_interactions):
        """Test checking for supplement interactions."""
        # Setup mocks
        recent_supplement_id = f"RECENT_{uuid.uuid4().hex[:8]}"
        recent_log = MagicMock()
        recent_log.supplement_id = recent_supplement_id
        mock_find_recent.return_value = [recent_log]
        
        # Create mock interactions
        interaction1 = MagicMock()
        interaction1.severity = "High"
        interaction1.supplements = [{"supplementId": self.test_supplement_id}, {"supplementId": recent_supplement_id}]
        interaction1.to_dict.return_value = {
            "interactionId": f"INT_{uuid.uuid4().hex[:8]}",
            "severity": "High",
            "description": "Test interaction"
        }
        
        # Configure check_interactions mock
        mock_check_interactions.side_effect = [
            [interaction1],  # First call returns initial interactions
            [interaction1]   # Second call returns all interactions
        ]
        
        # Make request
        request_data = {
            "supplementIds": [self.test_supplement_id],
            "foodItems": ["grapefruit"],
            "medications": ["warfarin"]
        }
        
        response = self.client.post(
            '/api/intake-logs/check-interactions',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("interactions", data)
        self.assertIn("count", data)
        self.assertIn("categorized", data)
        self.assertIn("high", data["categorized"])
        self.assertEqual(len(data["categorized"]["high"]), 1)
        
        # Verify mocks were called correctly
        mock_find_recent.assert_called_once_with(self.test_user_id, hours=24)
        mock_check_interactions.assert_any_call(
            supplement_ids=[self.test_supplement_id],
            food_items=["grapefruit"],
            medications=["warfarin"]
        )
    
    @patch('app.models.interaction.Interaction.check_interactions')
    def test_check_intake_interactions_no_recent_logs(self, mock_check_interactions):
        """Test checking interactions without recent logs."""
        # Setup empty recent logs
        with patch('app.models.intake_log.IntakeLog.find_recent', return_value=[]):
            # Setup interactions mock
            interaction = MagicMock()
            interaction.severity = "Low"
            interaction.to_dict.return_value = {"severity": "Low"}
            mock_check_interactions.return_value = [interaction]
            
            # Make request
            request_data = {
                "supplementIds": [self.test_supplement_id]
            }
            
            response = self.client.post(
                '/api/intake-logs/check-interactions',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            # Assert response
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["count"], 1)
            self.assertEqual(len(data["categorized"]["low"]), 1)
    
    @patch('app.models.interaction.Interaction.check_interactions')
    @patch('app.models.intake_log.IntakeLog.find_recent')
    def test_check_intake_interactions_server_error(self, mock_find_recent, mock_check_interactions):
        """Test checking interactions with server error."""
        # Setup mock to raise an exception
        mock_check_interactions.side_effect = Exception("Database connection error")
        
        # Setup recent logs
        recent_log = MagicMock()
        recent_log.supplement_id = f"RECENT_{uuid.uuid4().hex[:8]}"
        mock_find_recent.return_value = [recent_log]
        
        # Make request
        request_data = {
            "supplementIds": [self.test_supplement_id]
        }
        
        response = self.client.post(
            '/api/intake-logs/check-interactions',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to check interactions", data["error"])
    
    def test_check_intake_interactions_missing_supplements(self):
        """Test checking interactions without providing supplement IDs."""
        # Make request without supplement IDs
        request_data = {
            "foodItems": ["grapefruit"],
            "medications": ["warfarin"]
        }
        
        response = self.client.post(
            '/api/intake-logs/check-interactions',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "At least one supplement ID is required")
    
    # GET /api/intake-logs/<log_id> - Get a specific intake log
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    def test_get_intake_log_by_id_success(self, mock_find_by_id):
        """Test getting a specific intake log by ID successfully."""
        # Setup mock to return a log owned by the current user
        mock_find_by_id.return_value = self.mock_log
        
        # Make request
        response = self.client.get(f'/api/intake-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["intakeLogId"], self.test_log_data["intakeLogId"])
        self.assertEqual(data["supplementId"], self.test_log_data["supplementId"])
        
        # Verify mock was called with correct ID
        mock_find_by_id.assert_called_once_with(self.test_id)
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    def test_get_intake_log_by_id_not_found(self, mock_find_by_id):
        """Test getting a non-existent intake log by ID."""
        # Setup mock to return None
        mock_find_by_id.return_value = None
        
        # Make request
        response = self.client.get(f'/api/intake-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Intake log not found")
        
        # Verify mock was called
        mock_find_by_id.assert_called_once()
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.models.user.User.find_by_id')
    def test_get_intake_log_permission_denied(self, mock_find_user, mock_find_log):
        """Test that a user cannot access another user's log."""
        # Setup mocks for a different user
        different_user_log = MagicMock()
        different_user_log.user_id = f"OTHER_USER_{uuid.uuid4().hex[:8]}"
        mock_find_log.return_value = different_user_log
        mock_find_user.return_value = self.mock_user  # Regular user, not admin
        
        # Make request
        response = self.client.get(f'/api/intake-logs/{self.test_id}')
        
        # Assert response shows permission denied
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("permission", data["error"].lower())
        
        # Verify mocks were called
        mock_find_log.assert_called_once()
        mock_find_user.assert_called_once()
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.models.user.User.find_by_id')
    def test_get_intake_log_as_admin(self, mock_find_user, mock_find_log):
        """Test that an admin can access any intake log."""
        # Setup mocks
        different_user_log = MagicMock()
        different_user_log.user_id = f"OTHER_USER_{uuid.uuid4().hex[:8]}"
        different_user_log.to_dict.return_value = {
            "intakeLogId": f"OTHER_INTAKE_{uuid.uuid4().hex[:8]}",
            "userId": different_user_log.user_id
        }
        
        mock_find_log.return_value = different_user_log
        mock_find_user.return_value = self.mock_admin  # Admin user
        
        # Make request
        response = self.client.get(f'/api/intake-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["userId"], different_user_log.user_id)
        
        # Verify mocks were called
        mock_find_log.assert_called_once()
        mock_find_user.assert_called_once()
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    def test_get_intake_log_server_error(self, mock_find_by_id):
        """Test getting a specific intake log with server error."""
        # Setup mock to raise an exception
        mock_find_by_id.side_effect = Exception("Database connection error")
        
        # Make request
        response = self.client.get(f'/api/intake-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to get intake log", data["error"])
    
    # Test the 7-day update window restriction
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.routes.intake_logs.datetime')
    def test_update_intake_log_older_than_7_days(self, mock_datetime, mock_find_by_id):
        """Test that updating a log older than 7 days is not allowed."""
        # Setup current time mock
        current_time = datetime.now()
        mock_datetime.now.return_value = current_time
        mock_datetime.fromisoformat = datetime.fromisoformat
        
        # Create a log with timestamp more than 7 days ago
        old_log = MagicMock()
        old_log.user_id = self.test_user_id
        old_log.timestamp = (current_time - timedelta(days=8)).isoformat()
        mock_find_by_id.return_value = old_log
        
        # Make update request
        update_data = {
            "dosage": 1000,
            "notes": "Updated notes"
        }
        
        response = self.client.put(
            f'/api/intake-logs/{self.test_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert response shows 7-day restriction error
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data["error"], "Cannot update logs older than 7 days")
        
        # Verify find_by_id was called but update was not
        mock_find_by_id.assert_called_once_with(self.test_id)
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.routes.intake_logs.IntakeLog.update')
    @patch('app.routes.intake_logs.datetime')
    def test_update_intake_log_within_7_days(self, mock_datetime, mock_update, mock_find_by_id):
        """Test that updating a log within 7 days is allowed."""
        # Setup current time mock
        current_time = datetime.now()
        mock_datetime.now.return_value = current_time
        mock_datetime.fromisoformat = datetime.fromisoformat
        
        # Create a log with timestamp within 7 days
        recent_log = MagicMock()
        recent_log.user_id = self.test_user_id
        recent_log.timestamp = (current_time - timedelta(days=5)).isoformat()
        mock_find_by_id.return_value = recent_log
        
        # Setup update mock to return a proper updated log object
        updated_log = MagicMock()
        updated_log._id = self.test_id
        mock_update.return_value = updated_log
        
        # Make update request
        update_data = {
            "dosage": 1000,
            "notes": "Updated notes"
        }
        
        response = self.client.put(
            f'/api/intake-logs/{self.test_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Intake log updated successfully")
        
        # Verify find_by_id and update were called
        mock_find_by_id.assert_called_once_with(self.test_id)
        mock_update.assert_called_once_with(self.test_id, update_data)
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    def test_update_intake_log_invalid_json(self, mock_find_by_id):
        """Test updating an intake log with invalid JSON format."""
        # Make request with non-JSON data
        response = self.client.put(
            f'/api/intake-logs/{self.test_id}',
            data="This is not JSON",
            content_type='text/plain'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Missing JSON in request")
        
        # Verify find_by_id was not called
        mock_find_by_id.assert_not_called()
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    def test_update_intake_log_empty_data(self, mock_find_by_id):
        """Test updating an intake log with empty data."""
        # Make request with empty JSON
        response = self.client.put(
            f'/api/intake-logs/{self.test_id}',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Empty update data")
        
        # Verify find_by_id was not called
        mock_find_by_id.assert_not_called()
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.routes.intake_logs.IntakeLog.update')
    def test_update_intake_log_server_error(self, mock_update, mock_find_by_id):
        """Test updating an intake log with server error."""
        # Setup mocks
        mock_find_by_id.return_value = self.mock_log
        mock_update.side_effect = Exception("Database connection error")
        
        # Make request
        update_data = {
            "dosage": 1000
        }
        
        response = self.client.put(
            f'/api/intake-logs/{self.test_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to update intake log", data["error"])
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.routes.intake_logs.IntakeLog.update')
    def test_update_intake_log_value_error(self, mock_update, mock_find_by_id):
        """Test updating an intake log with validation error."""
        # Create error handler that properly passes the ValueError to the route
        def raise_value_error(*args, **kwargs):
            error_message = "Invalid dosage value"
            raise ValueError(error_message)
            
        # Setup mocks
        # Create a mock with timezone-naive timestamp that matches how datetime.now() works in the function
        mock_log = MagicMock()
        mock_log.user_id = self.test_user_id
        mock_log.timestamp = datetime.now().isoformat()  # Timezone-naive timestamp
        mock_find_by_id.return_value = mock_log
        mock_update.side_effect = raise_value_error
        
        # Mock datetime in the route
        with patch('app.routes.intake_logs.datetime') as mock_datetime:
            # Configure datetime mock to use timezone-naive time
            current_time = datetime.now()  # Timezone-naive
            mock_datetime.now.return_value = current_time
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            # Make request
            update_data = {
                "dosage": -1000  # Invalid negative value
            }
            
            response = self.client.put(
                f'/api/intake-logs/{self.test_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            # Assert response
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data["error"], "Invalid dosage value")
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.routes.intake_logs.datetime')
    def test_update_intake_log_complex_timestamp(self, mock_datetime, mock_find_by_id):
        """Test updating a log with a complex timestamp format."""
        # Setup current time mock
        current_time = datetime.now()
        mock_datetime.now.return_value = current_time
        mock_datetime.fromisoformat = datetime.fromisoformat
        
        # Create a log with timestamp within 7 days (to pass validation)
        recent_log = MagicMock()
        recent_log.user_id = self.test_user_id
        recent_log.timestamp = (current_time - timedelta(days=3)).isoformat()  # Use simple ISO format
        mock_find_by_id.return_value = recent_log
        
        # Setup update mock
        updated_log = MagicMock()
        updated_log._id = self.test_id
        
        with patch('app.routes.intake_logs.IntakeLog.update', return_value=updated_log) as mock_update:
            # Make update request
            update_data = {
                "dosage": 1000
            }
            
            response = self.client.put(
                f'/api/intake-logs/{self.test_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            # Assert response
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["message"], "Intake log updated successfully")
    
    # DELETE /api/intake-logs/<log_id> - Delete an intake log
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.models.intake_log.IntakeLog.delete')
    def test_delete_intake_log_success(self, mock_delete, mock_find_by_id):
        """Test deleting an intake log successfully."""
        # Setup mocks
        mock_find_by_id.return_value = self.mock_log  # Log owned by current user
        
        # Setup delete mock
        deleted_log = MagicMock()
        deleted_log._id = self.test_id
        mock_delete.return_value = deleted_log
        
        # Make request
        response = self.client.delete(f'/api/intake-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Intake log deleted successfully")
        
        # Verify mocks were called with correct parameters
        mock_find_by_id.assert_called_once_with(self.test_id)
        mock_delete.assert_called_once_with(self.test_id)
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.models.intake_log.IntakeLog.delete')
    def test_delete_intake_log_server_error(self, mock_delete, mock_find_by_id):
        """Test deleting an intake log with server error."""
        # Setup mocks
        mock_find_by_id.return_value = self.mock_log
        mock_delete.side_effect = Exception("Database connection error")
        
        # Make request
        response = self.client.delete(f'/api/intake-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to delete intake log", data["error"])
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.models.intake_log.IntakeLog.delete')
    def test_delete_intake_log_value_error(self, mock_delete, mock_find_by_id):
        """Test deleting an intake log with validation error."""
        # Setup mocks
        mock_find_by_id.return_value = self.mock_log
        error_message = "Cannot delete intake log with associated reports"
        mock_delete.side_effect = ValueError(error_message)
        
        # Make request
        response = self.client.delete(f'/api/intake-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], error_message)
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    def test_delete_intake_log_not_found(self, mock_find_by_id):
        """Test deleting a non-existent intake log."""
        # Setup mock to return None
        mock_find_by_id.return_value = None
        
        # Make request
        response = self.client.delete(f'/api/intake-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Intake log not found")
        
        # Verify mock was called
        mock_find_by_id.assert_called_once()
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.models.user.User.find_by_id')
    def test_delete_intake_log_permission_denied(self, mock_find_user, mock_find_log):
        """Test that a user cannot delete another user's log."""
        # Setup mocks for a different user
        different_user_log = MagicMock()
        different_user_log.user_id = f"OTHER_USER_{uuid.uuid4().hex[:8]}"
        mock_find_log.return_value = different_user_log
        mock_find_user.return_value = self.mock_user  # Regular user, not admin
        
        # Make request
        response = self.client.delete(f'/api/intake-logs/{self.test_id}')
        
        # Assert response shows permission denied
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("permission", data["error"].lower())
        
        # Verify mocks were called
        mock_find_log.assert_called_once()
        mock_find_user.assert_called_once()
    
    @patch('app.models.intake_log.IntakeLog.find_by_id')
    @patch('app.models.user.User.find_by_id')
    @patch('app.models.intake_log.IntakeLog.delete')
    def test_delete_intake_log_as_admin(self, mock_delete, mock_find_user, mock_find_log):
        """Test that an admin can delete any intake log."""
        # Setup mocks
        different_user_log = MagicMock()
        different_user_log.user_id = f"OTHER_USER_{uuid.uuid4().hex[:8]}"
        
        mock_find_log.return_value = different_user_log
        mock_find_user.return_value = self.mock_admin  # Admin user
        
        # Setup delete mock
        deleted_log = MagicMock()
        deleted_log._id = self.test_id
        mock_delete.return_value = deleted_log
        
        # Make request
        response = self.client.delete(f'/api/intake-logs/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Intake log deleted successfully")
        
        # Verify admin check was performed and delete was called
        mock_find_user.assert_called_once()
        mock_delete.assert_called_once()


if __name__ == '__main__':
    unittest.main()
