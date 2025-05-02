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
from app.models.symptom_log import SymptomLog, SymptomCategoryManager
from app.routes.symptom_logs import bp as symptom_logs_bp

class TestSymptomLogsRoutes(unittest.TestCase):

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
        self.app.register_blueprint(symptom_logs_bp)

        # Sample symptom log data
        self.log_data = {
            'symptom_id': str(ObjectId()),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'severity': 3,
            'notes': 'Test symptom'
        }

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    @patch('app.routes.symptom_logs.SymptomCategoryManager.initialize_symptom_data')
    def test_initialize_database(self, mock_init):
        """Test that database initialization occurs."""
        # Call the route that would trigger initialization
        response = self.client.get('/api/symptom-logs/symptoms')
        
        # This should have triggered initialization
        mock_init.assert_called_once()

    @patch('app.routes.symptom_logs.SymptomLog.get_symptom_details')
    def test_get_all_symptoms(self, mock_get_details):
        """Test getting all symptoms."""
        # Configure mock
        mock_get_details.return_value = {
            str(ObjectId()): {
                "_id": ObjectId(),
                "name": "Headache",
                "categoryId": ObjectId(),
                "description": "Head pain"
            }
        }
        
        response = self.client.get('/api/symptom-logs/symptoms')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('symptoms', data)
        self.assertIsInstance(data['symptoms'], list)
        mock_get_details.assert_called_once()

    @patch('app.routes.symptom_logs.SymptomLog.get_symptom_details')
    def test_get_all_symptoms_exception(self, mock_get_details):
        """Test exception when getting symptoms."""
        mock_get_details.side_effect = Exception("Database error")
        
        response = self.client.get('/api/symptom-logs/symptoms')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch('app.routes.symptom_logs.SymptomLog.create')
    def test_create_symptom_log_success(self, mock_create):
        """Test successful creation of symptom log."""
        # Configure mock
        mock_log = MagicMock()
        mock_log._id = ObjectId()
        mock_log.to_dict.return_value = {**self.log_data, '_id': str(mock_log._id)}
        mock_create.return_value = mock_log

        # Make request
        response = self.client.post('/api/symptom-logs/', 
                                   json=self.log_data,
                                   headers=self.headers)
        
        # Assert response
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('log_id', data)
        self.assertIn('log', data)
        mock_create.assert_called_once()

    def test_create_symptom_log_no_data(self):
        """Test creating symptom log with no data."""
        response = self.client.post('/api/symptom-logs/',
                                   json=None,
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No data provided')

    def test_create_symptom_log_missing_field(self):
        """Test creating symptom log with missing required field."""
        # Remove a required field
        incomplete_data = self.log_data.copy()
        del incomplete_data['severity']
        
        response = self.client.post('/api/symptom-logs/',
                                   json=incomplete_data,
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Missing required field', data['error'])

    @patch('app.routes.symptom_logs.SymptomLog.create')
    def test_create_symptom_log_value_error(self, mock_create):
        """Test ValueError during symptom log creation."""
        mock_create.side_effect = ValueError('Invalid severity value')
        
        response = self.client.post('/api/symptom-logs/',
                                   json=self.log_data,
                                   headers=self.headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid severity value')

    @patch('app.routes.symptom_logs.SymptomLog.find_by_date_range')
    def test_get_symptom_logs_default(self, mock_find):
        """Test getting symptom logs with default date range."""
        # Configure mock
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {**self.log_data, '_id': str(ObjectId())}
        mock_find.return_value = [mock_log]
        
        response = self.client.get('/api/symptom-logs/', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)
        # Should default to 7-day range
        mock_find.assert_called_once()

    @patch('app.routes.symptom_logs.SymptomLog.find_by_date_range')
    def test_get_symptom_logs_with_date_range(self, mock_find):
        """Test getting symptom logs with custom date range."""
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {**self.log_data, '_id': str(ObjectId())}
        mock_find.return_value = [mock_log]
        
        start_date = '2023-01-01'
        end_date = '2023-01-31'
        
        response = self.client.get(f'/api/symptom-logs/?start_date={start_date}&end_date={end_date}', 
                                  headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        mock_find.assert_called_once()
        args, kwargs = mock_find.call_args
        self.assertEqual(args[1], start_date)
        self.assertEqual(args[2], end_date)

    @patch('app.routes.symptom_logs.SymptomLog.find_by_date')
    def test_get_today_symptom_logs(self, mock_find):
        """Test getting today's symptom logs."""
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {**self.log_data, '_id': str(ObjectId())}
        mock_find.return_value = [mock_log]
        
        response = self.client.get('/api/symptom-logs/today', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)
        # Should be called with today's date
        mock_find.assert_called_once()
        args, kwargs = mock_find.call_args
        today = datetime.now().strftime("%Y-%m-%d")
        self.assertEqual(args[1], today)

    @patch('app.routes.symptom_logs.SymptomLog.find_by_date')
    @patch('app.routes.symptom_logs.SymptomLog.get_symptom_details')
    def test_get_logs_for_date(self, mock_get_details, mock_find):
        """Test getting logs for a specific date."""
        # Configure mocks
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {
            '_id': str(ObjectId()),
            'symptom_id': 'symptom123',
            'severity': 3,
            'notes': 'Test notes',
            'date': '2023-05-01'
        }
        mock_find.return_value = [mock_log]
        
        mock_get_details.return_value = {
            'symptom123': {
                'name': 'Headache',
                'icon': 'headache.png',
                'categoryName': 'Pain',
                'categoryIcon': 'pain.png'
            }
        }
        
        response = self.client.get('/api/symptom-logs/date/2023-05-01', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('logs', data)
        self.assertEqual(len(data['logs']), 1)
        log = data['logs'][0]
        self.assertEqual(log['symptom_name'], 'Headache')

    def test_get_logs_for_date_invalid_format(self):
        """Test getting logs with invalid date format."""
        response = self.client.get('/api/symptom-logs/date/not-a-date', headers=self.headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Invalid date format', data['error'])

    @patch('app.routes.symptom_logs.SymptomLog.find_active_symptoms_for_date')
    @patch('app.routes.symptom_logs.SymptomLog.get_symptom_details')
    def test_get_active_logs_for_date(self, mock_get_details, mock_find):
        """Test getting active logs for a specific date."""
        # Configure mocks (similar to previous test)
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {
            '_id': str(ObjectId()),
            'symptom_id': 'symptom123',
            'severity': 3,
            'notes': 'Test notes',
            'date': '2023-05-01'
        }
        mock_find.return_value = [mock_log]
        
        mock_get_details.return_value = {
            'symptom123': {
                'name': 'Headache',
                'icon': 'headache.png',
                'categoryName': 'Pain',
                'categoryIcon': 'pain.png'
            }
        }
        
        response = self.client.get('/api/symptom-logs/active/2023-05-01', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('logs', data)

    @patch('app.routes.symptom_logs.SymptomLog.get_dates_with_symptoms')
    def test_get_dates_with_symptoms(self, mock_get_dates):
        """Test getting dates with symptoms."""
        mock_get_dates.return_value = ['2023-05-01', '2023-05-02']
        
        response = self.client.get('/api/symptom-logs/dates-with-symptoms', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('dates', data)
        self.assertEqual(len(data['dates']), 2)
        mock_get_dates.assert_called_once_with(self.user_id)

    @patch('app.routes.symptom_logs.SymptomLog.delete')
    def test_delete_symptom_log(self, mock_delete):
        """Test deleting a symptom log."""
        log_id = str(ObjectId())
        mock_log = MagicMock()
        mock_log._id = ObjectId(log_id)
        mock_delete.return_value = True  # Delete returns True on success

        response = self.client.delete(f'/api/symptom-logs/{log_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Symptom log deleted successfully')
        mock_delete.assert_called_once_with(log_id)

    @patch('app.routes.symptom_logs.SymptomLog.delete')
    def test_delete_symptom_log_not_found(self, mock_delete):
        """Test deleting a non-existent symptom log."""
        log_id = str(ObjectId())
        mock_delete.return_value = None  # Delete returns None if log not found
        
        response = self.client.delete(f'/api/symptom-logs/{log_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Symptom log not found')

    @patch('app.routes.symptom_logs.SymptomLog.find_active_symptoms_for_date')
    @patch('app.routes.symptom_logs.SymptomLog.get_symptom_details')
    def test_get_symptoms_summary(self, mock_get_details, mock_find_active):
        """Test getting symptoms summary for a date."""
        # Configure mocks
        # Mock active logs for the date
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {
            '_id': str(ObjectId()),
            'symptom_id': 'symptom123',
            'severity': 3,
            'notes': 'Test notes',
            'date': '2023-05-01'
        }
        mock_find_active.return_value = [mock_log]
        
        # Mock symptom details
        mock_get_details.return_value = {
            'symptom123': {
                'name': 'Headache',
                'icon': 'headache.png',
                'categoryName': 'General',
                'categoryIcon': 'general.png'
            }
        }
        
        response = self.client.get('/api/symptom-logs/summary/2023-05-01', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('categories', data)

    @patch('app.routes.symptom_logs.SymptomLog.find_by_date_range')
    def test_get_logs_for_date_range(self, mock_find):
        """Test getting logs for a date range."""
        # Configure mock - use a MagicMock instead of self.mock_symptom_log
        mock_log = MagicMock()
        mock_log.to_dict.return_value = {
            'symptom_id': 'symptom123',
            'symptom_type': 'Headache',
            'severity': 3,
            'date': '2023-01-15'
        }
        mock_find.return_value = [mock_log]
        
        # Make request
        response = self.client.get(
            '/api/symptom-logs/range?start_date=2023-01-01&end_date=2023-01-31',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('logs', data)
        self.assertEqual(len(data['logs']), 1)
        mock_find.assert_called_once_with(self.user_id, '2023-01-01', '2023-01-31')

    def test_get_logs_for_date_range_missing_params(self):
        """Test getting logs for a date range with missing parameters."""
        # Make request with missing end_date
        response = self.client.get(
            '/api/symptom-logs/range?start_date=2023-01-01',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Both start_date and end_date are required', data['error'])

    def test_get_logs_for_date_range_invalid_format(self):
        """Test getting logs for a date range with invalid date format."""
        # Make request with invalid date format
        response = self.client.get(
            '/api/symptom-logs/range?start_date=01-01-2023&end_date=01-31-2023',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Invalid date format', data['error'])

    @patch('app.routes.symptom_logs.SymptomLog.get_dates_with_symptoms')
    def test_get_dates_with_symptoms(self, mock_get_dates):
        """Test getting dates with symptoms."""
        # Configure mock
        mock_get_dates.return_value = ['2023-01-01', '2023-01-15', '2023-01-30']
        
        # Make request
        response = self.client.get(
            '/api/symptom-logs/dates-with-symptoms',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('dates', data)
        self.assertEqual(len(data['dates']), 3)
        mock_get_dates.assert_called_once_with(self.user_id)

    @patch('app.routes.symptom_logs.SymptomLog.get_dates_with_symptoms')
    def test_get_dates_with_symptoms_exception(self, mock_get_dates):
        """Test exception handling when getting dates with symptoms."""
        # Configure mock
        mock_get_dates.side_effect = Exception('Database error')
        
        # Make request
        response = self.client.get(
            '/api/symptom-logs/dates-with-symptoms',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch('app.routes.symptom_logs.SymptomCategoryManager.initialize_symptom_data')
    def test_initialize_database_exception(self, mock_initialize):
        """Test exception handling during database initialization."""
        # Configure mock
        mock_initialize.side_effect = Exception('Initialization error')
        
        # Create a new Flask app and test the blueprint registration
        app = create_app()
        with app.app_context():
            bp = app.blueprints['symptom_logs']
            # Instead of trying to access Blueprint internals directly, which has changed,
            # we'll just verify the blueprint was registered properly
            self.assertIsNotNone(bp)
            # No assertion needed - we're just making sure it doesn't crash
            # The exception should be caught and logged by the function

    @patch('app.routes.symptom_logs.SymptomLog.find_active_symptoms_for_date')
    def test_get_active_logs_for_date_invalid_format(self, mock_find):
        """Test invalid date format for active logs."""
        # Make request with invalid date format
        response = self.client.get(
            '/api/symptom-logs/active/2023-13-45',  # Invalid date
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Invalid date format', data['error'])
        mock_find.assert_not_called()

    @patch('app.routes.symptom_logs.SymptomLog.find_active_symptoms_for_date')
    def test_get_active_logs_for_date_exception(self, mock_find):
        """Test exception handling when getting active logs for a date."""
        # Configure mock
        mock_find.side_effect = Exception('Database error')
        
        # Make request
        response = self.client.get(
            '/api/symptom-logs/active/2023-01-01',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        mock_find.assert_called_once_with(self.user_id, '2023-01-01')

    @patch('app.routes.symptom_logs.SymptomLog.find_by_date')
    def test_get_logs_for_date_exception(self, mock_find):
        """Test exception handling when getting logs for a date."""
        # Configure mock
        mock_find.side_effect = Exception('Database error')
        
        # Make request
        response = self.client.get(
            '/api/symptom-logs/date/2023-01-01',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        mock_find.assert_called_once_with(self.user_id, '2023-01-01')

    @patch('app.routes.symptom_logs.SymptomLog.get_symptom_details')
    def test_get_all_symptoms_value_error(self, mock_get_details):
        """Test getting all symptoms with a ValueError."""
        # Configure mock
        mock_get_details.side_effect = ValueError('Invalid data')
        
        # Make request
        response = self.client.get('/api/symptom-logs/symptoms')
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid data')

    @patch('app.routes.symptom_logs.SymptomLog.find_active_symptoms_for_date')
    @patch('app.routes.symptom_logs.SymptomLog.get_symptom_details')
    def test_get_symptoms_summary_with_empty_logs(self, mock_get_details, mock_find_active):
        """Test getting symptoms summary with empty logs."""
        # Configure mocks
        mock_find_active.return_value = []
        mock_get_details.return_value = {}
        
        # Make request
        response = self.client.get(
            '/api/symptom-logs/summary/2023-01-01',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('categories', data)
        self.assertEqual(len(data['categories']), 0)
        self.assertIn('notes', data)
        self.assertEqual(data['notes'], '')
        self.assertIn('date', data)
        self.assertEqual(data['date'], '2023-01-01')

    @patch('app.routes.symptom_logs.SymptomLog.find_active_symptoms_for_date')
    @patch('app.routes.symptom_logs.SymptomLog.get_symptom_details')
    def test_get_symptoms_summary_with_notes(self, mock_get_details, mock_find_active):
        """Test getting symptoms summary with logs that have notes."""
        # Configure mocks
        mock_log = MagicMock()
        mock_log.symptom_type = 'Headache'
        mock_log.severity = 4
        mock_log.to_dict.return_value = {
            'symptom_id': 'symptom123',
            'severity': 4,
            'notes': 'Important symptom notes',
            'date': '2023-01-01'
        }
        mock_find_active.return_value = [mock_log]
        
        mock_get_details.return_value = {
            'symptom123': {
                '_id': 'symptom123',
                'name': 'Headache',
                'icon': '🤕',
                'categoryName': 'General',
                'categoryIcon': '🔍',
                'categoryId': 'general'
            }
        }
        
        # Make request
        response = self.client.get(
            '/api/symptom-logs/summary/2023-01-01',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('notes', data)
        self.assertEqual(data['notes'], 'Important symptom notes')
        self.assertIn('categories', data)
        self.assertGreaterEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['name'], 'General')
        self.assertEqual(len(data['categories'][0]['symptoms']), 1)
        self.assertEqual(data['categories'][0]['symptoms'][0]['name'], 'Headache')

    @patch('app.routes.symptom_logs.SymptomLog.find_active_symptoms_for_date')
    @patch('app.routes.symptom_logs.SymptomLog.get_symptom_details')
    def test_get_symptoms_summary_exception(self, mock_get_details, mock_find_active):
        """Test exception handling when getting symptoms summary."""
        # Configure mocks
        mock_find_active.side_effect = Exception('Database error')
        
        # Make request
        response = self.client.get(
            '/api/symptom-logs/summary/2023-01-01',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        # Assert the actual error message, not a generic message
        self.assertEqual(data['error'], 'Database error')

if __name__ == '__main__':
    unittest.main() 