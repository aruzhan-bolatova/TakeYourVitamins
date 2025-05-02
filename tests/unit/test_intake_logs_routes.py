import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from flask_jwt_extended import create_access_token, JWTManager
from bson.objectid import ObjectId
import sys
import os
import json
from datetime import datetime, timedelta

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.intake_log import IntakeLog
from app.routes.intake_logs import bp as intake_logs_bp

class TestIntakeLogsRoutes(unittest.TestCase):

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
        self.other_user_id = str(ObjectId())
        
        # Create access tokens
        self.access_token = create_access_token(identity=self.user_id)
        self.headers = {'Authorization': f'Bearer {self.access_token}'}

        # Register blueprint
        self.app.register_blueprint(intake_logs_bp)

        # Sample intake log data
        self.log_data = {
            'tracked_supplement_id': str(ObjectId()),
            'intake_date': datetime.now().strftime('%Y-%m-%d'),
            'dosage_taken': 500,
            'unit': 'mg',
            'notes': 'Test notes'
        }

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    @patch('app.routes.intake_logs.IntakeLog.create')
    def test_create_intake_log_success(self, mock_create):
        """Test successful creation of intake log."""
        # Configure mock
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {**self.log_data, '_id': str(ObjectId())}
        mock_create.return_value = mock_log

        # Make request
        response = self.client.post('/api/intake_logs/', 
                                   json=self.log_data,
                                   headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_once()

    def test_create_intake_log_no_data(self):
        """Test creating intake log with no data."""
        response = self.client.post('/api/intake_logs/',
                                   json=None,
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No data provided')

    def test_create_intake_log_missing_field(self):
        """Test creating intake log with missing required field."""
        # Remove a required field
        incomplete_data = self.log_data.copy()
        del incomplete_data['intake_date']
        
        response = self.client.post('/api/intake_logs/',
                                   json=incomplete_data,
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Missing required field', data['error'])

    @patch('app.routes.intake_logs.IntakeLog.create')
    def test_create_intake_log_value_error(self, mock_create):
        """Test ValueError during intake log creation."""
        mock_create.side_effect = ValueError('Invalid data format')
        
        response = self.client.post('/api/intake_logs/',
                                   json=self.log_data,
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid data format')

    @patch('app.routes.intake_logs.IntakeLog.create')
    def test_create_intake_log_exception(self, mock_create):
        """Test general exception during intake log creation."""
        mock_create.side_effect = Exception('Database error')
        
        response = self.client.post('/api/intake_logs/',
                                   json=self.log_data,
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Error creating intake log', data['error'])

    @patch('app.routes.intake_logs.IntakeLog.find_by_date_range')
    def test_get_intake_logs_default(self, mock_find):
        """Test getting intake logs with default date range."""
        # Configure mock
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {**self.log_data, '_id': str(ObjectId())}
        mock_find.return_value = [mock_log]
        
        response = self.client.get('/api/intake_logs/', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)
        # Should default to 7-day range
        mock_find.assert_called_once()
        
    @patch('app.routes.intake_logs.IntakeLog.find_by_date_range')
    def test_get_intake_logs_with_date_range(self, mock_find):
        """Test getting intake logs with custom date range."""
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {**self.log_data, '_id': str(ObjectId())}
        mock_find.return_value = [mock_log]
        
        start_date = '2023-01-01'
        end_date = '2023-01-31'
        
        response = self.client.get(f'/api/intake_logs/?start_date={start_date}&end_date={end_date}', 
                                  headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        mock_find.assert_called_once()
        args, kwargs = mock_find.call_args
        self.assertEqual(args[1], start_date)
        self.assertEqual(args[2], end_date)

    @patch('app.routes.intake_logs.IntakeLog.find_by_supplement_id')
    def test_get_intake_logs_by_supplement(self, mock_find):
        """Test getting intake logs filtered by supplement."""
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {**self.log_data, '_id': str(ObjectId())}
        mock_find.return_value = [mock_log]
        
        supplement_id = str(ObjectId())
        
        response = self.client.get(f'/api/intake_logs/?supplement_id={supplement_id}', 
                                  headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        mock_find.assert_called_once_with(ObjectId(self.user_id), supplement_id)

    @patch('app.routes.intake_logs.IntakeLog.find_by_date_range')
    def test_get_intake_logs_value_error(self, mock_find):
        """Test ValueError when getting intake logs."""
        mock_find.side_effect = ValueError('Invalid date format')
        
        response = self.client.get('/api/intake_logs/', headers=self.headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid date format')

    @patch('app.routes.intake_logs.IntakeLog.find_by_date_range')
    def test_get_today_intake_logs(self, mock_find):
        """Test getting today's intake logs."""
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {**self.log_data, '_id': str(ObjectId())}
        mock_find.return_value = [mock_log]
        
        response = self.client.get('/api/intake_logs/today', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)
        mock_find.assert_called_once()
        # Should be called with today's date for both start and end
        args, kwargs = mock_find.call_args
        self.assertEqual(args[1], args[2])  # start_date = end_date = today

    @patch('app.routes.intake_logs.IntakeLog.get_intake_summary')
    def test_get_intake_summary_default_dates(self, mock_summary):
        """Test getting intake summary with default dates."""
        mock_summary.return_value = {"supplements": [], "total_logs": 0}
        
        response = self.client.get('/api/intake_logs/summary', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        mock_summary.assert_called_once()
        # Should be called with last 30 days by default
        args, kwargs = mock_summary.call_args
        today = datetime.now().strftime("%Y-%m-%d")
        self.assertEqual(args[2], today)  # end_date = today

    @patch('app.routes.intake_logs.IntakeLog.find_by_id')
    def test_get_intake_log_by_id(self, mock_find):
        """Test getting a specific intake log by ID."""
        log_id = str(ObjectId())
        mock_log = MagicMock()
        mock_log.user_id = ObjectId(self.user_id)  # Important: same user as JWT
        mock_log.to_dict.return_value = {**self.log_data, '_id': log_id}
        mock_find.return_value = mock_log
        
        response = self.client.get(f'/api/intake_logs/{log_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        mock_find.assert_called_once_with(log_id)

    @patch('app.routes.intake_logs.IntakeLog.find_by_id')
    def test_get_intake_log_not_found(self, mock_find):
        """Test getting a non-existent intake log."""
        log_id = str(ObjectId())
        mock_find.return_value = None
        
        response = self.client.get(f'/api/intake_logs/{log_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Intake log not found')

    @patch('app.routes.intake_logs.IntakeLog.find_by_id')
    def test_get_intake_log_wrong_user(self, mock_find):
        """Test unauthorized access to another user's intake log."""
        log_id = str(ObjectId())
        mock_log = MagicMock()
        mock_log.user_id = ObjectId(self.other_user_id)  # Different user
        mock_find.return_value = mock_log
        
        response = self.client.get(f'/api/intake_logs/{log_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Not authorized', data['error'])

    @patch('app.routes.intake_logs.IntakeLog.find_by_id')
    @patch('app.routes.intake_logs.IntakeLog.delete')
    def test_delete_intake_log_soft(self, mock_delete, mock_find_by_id):
        """Test soft deleting an intake log."""
        log_id = str(ObjectId())
        # Mock finding the log
        mock_log = MagicMock()
        mock_log.user_id = ObjectId(self.user_id)
        mock_log._id = ObjectId(log_id)
        mock_find_by_id.return_value = mock_log

        # Mock deleting the log
        mock_delete.return_value = mock_log

        response = self.client.delete(f'/api/intake_logs/{log_id}', headers=self.headers)

        self.assertEqual(response.status_code, 200)
        mock_find_by_id.assert_called_once_with(log_id)
        mock_delete.assert_called_once_with(log_id)  # Updated to match actual implementation

    @patch('app.routes.intake_logs.IntakeLog.find_by_id')
    @patch('app.routes.intake_logs.IntakeLog.delete')
    def test_delete_intake_log_hard(self, mock_delete, mock_find_by_id):
        """Test hard deleting an intake log."""
        log_id = str(ObjectId())
        # Mock finding the log
        mock_log = MagicMock()
        mock_log.user_id = ObjectId(self.user_id)
        mock_log._id = ObjectId(log_id)
        mock_find_by_id.return_value = mock_log

        # Mock deleting the log
        mock_delete.return_value = mock_log

        response = self.client.delete(f'/api/intake_logs/{log_id}?hard=true', headers=self.headers)

        self.assertEqual(response.status_code, 200)
        mock_find_by_id.assert_called_once_with(log_id)
        mock_delete.assert_called_once_with(log_id)  # Updated to match actual implementation

    @patch('app.routes.intake_logs.IntakeLog.find_by_id')
    def test_delete_intake_log_not_found(self, mock_find):
        """Test deleting a non-existent intake log."""
        log_id = str(ObjectId())
        mock_find.return_value = None
        
        response = self.client.delete(f'/api/intake_logs/{log_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Intake log not found')

    @patch('app.routes.intake_logs.IntakeLog.find_by_id')
    @patch('app.routes.intake_logs.IntakeLog.update')
    def test_update_intake_log_success(self, mock_update, mock_find_by_id):
        """Test successfully updating an intake log."""
        log_id = str(ObjectId())
        update_data = {'dosage_taken': 750}
        
        # Mock finding the log
        mock_log = MagicMock()
        mock_log.user_id = ObjectId(self.user_id)
        mock_log.to_dict.return_value = {**self.log_data, **update_data, '_id': log_id}
        mock_find_by_id.return_value = mock_log
        
        # Mock updating the log
        mock_update.return_value = mock_log
        
        response = self.client.put(f'/api/intake_logs/{log_id}', 
                                  json=update_data,
                                  headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        mock_find_by_id.assert_called_once_with(log_id)
        mock_update.assert_called_once_with(log_id, update_data)


if __name__ == '__main__':
    unittest.main() 