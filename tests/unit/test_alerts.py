import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from datetime import datetime
from bson.objectid import ObjectId

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app


class TestAlerts(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Sample user data
        self.user_id = 'USER123456789'
        
        # Sample alert data
        self.test_alert = {
            '_id': ObjectId('5f7d8e9f9f7d8e9f9f7d8e9f'),
            'alertId': 'ALERT123',
            'userId': self.user_id,
            'type': 'interaction',
            'title': 'Test Alert',
            'message': 'This is a test alert',
            'severity': 'medium',
            'read': False,
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': None
        }
        
        # Convert ObjectId to string for comparison
        self.test_alert_json = self.test_alert.copy()
        self.test_alert_json['_id'] = str(self.test_alert['_id'])
    
    def tearDown(self):
        """Tear down test fixtures after each test method is run."""
        self.app_context.pop()
    
    def get_auth_headers(self):
        """Helper to get authentication headers."""
        with patch('app.routes.auth.User.authenticate', return_value=MagicMock(user_id=self.user_id)):
            login_data = {'email': 'test@example.com', 'password': 'password123'}
            response = self.client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            token = json.loads(response.data)['access_token']
            return {'Authorization': f'Bearer {token}'}
    
    def test_get_alerts_unauthorized(self):
        """Test getting alerts without authentication."""
        # Make request
        response = self.client.get('/api/alerts/')
        
        # Assert response
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('msg', data)
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.routes.alerts.get_db')
    def test_get_alerts(self, mock_get_db, mock_get_jwt_identity):
        """Test getting alerts for a user."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.user_id
        
        # Create mock DB that returns our test alerts
        mock_db = MagicMock()
        mock_db.Alerts.find.return_value = [self.test_alert]
        mock_get_db.return_value = mock_db
        
        # Make request
        response = self.client.get(
            '/api/alerts/',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['alertId'], self.test_alert['alertId'])
        self.assertEqual(data[0]['_id'], str(self.test_alert['_id']))
        
        # Verify mock calls
        mock_get_db.assert_called_once()
        mock_db.Alerts.find.assert_called_once_with({'userId': self.user_id})
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.routes.alerts.get_db')
    def test_get_alerts_with_filter(self, mock_get_db, mock_get_jwt_identity):
        """Test getting alerts with filtering."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.user_id
        
        # Create mock DB that returns our test alerts
        mock_db = MagicMock()
        mock_db.Alerts.find.return_value = [self.test_alert]
        mock_get_db.return_value = mock_db
        
        # Make request
        response = self.client.get(
            '/api/alerts/?read=false',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        
        # Verify mock calls
        mock_get_db.assert_called_once()
        mock_db.Alerts.find.assert_called_once_with({'userId': self.user_id, 'read': False})
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.routes.alerts.get_db')
    def test_get_alerts_exception(self, mock_get_db, mock_get_jwt_identity):
        """Test error handling when getting alerts."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.user_id
        mock_get_db.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.get(
            '/api/alerts/',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Failed to get alerts')
        self.assertEqual(data['details'], 'Database error')
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.routes.alerts.get_db')
    def test_mark_alert_read(self, mock_get_db, mock_get_jwt_identity):
        """Test marking an alert as read."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.user_id
        
        # Create mock DB that returns our test alert
        mock_db = MagicMock()
        mock_db.Alerts.update_one.return_value = MagicMock(matched_count=1)
        mock_get_db.return_value = mock_db
        
        # Make request
        alert_id = str(self.test_alert['_id'])
        response = self.client.put(
            f'/api/alerts/{alert_id}',
            data=json.dumps({'read': True}),
            content_type='application/json',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Alert updated successfully')
        
        # Verify mock calls
        mock_get_db.assert_called_once()
        mock_db.Alerts.update_one.assert_called_once()
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.routes.alerts.get_db')
    def test_mark_alert_read_not_found(self, mock_get_db, mock_get_jwt_identity):
        """Test marking a non-existent alert as read."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.user_id
        
        # Create mock DB that returns no alerts
        mock_db = MagicMock()
        mock_db.Alerts.update_one.return_value = MagicMock(matched_count=0)
        mock_get_db.return_value = mock_db
        
        # Make request
        response = self.client.put(
            '/api/alerts/nonexistent',
            data=json.dumps({'read': True}),
            content_type='application/json',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Alert not found')
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.routes.alerts.get_db')
    def test_mark_alert_read_exception(self, mock_get_db, mock_get_jwt_identity):
        """Test error handling when marking an alert as read."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.user_id
        mock_get_db.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.put(
            f'/api/alerts/{str(self.test_alert["_id"])}',
            data=json.dumps({'read': True}),
            content_type='application/json',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Failed to update alert')
        self.assertEqual(data['details'], 'Database error')
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.routes.alerts.get_db')
    def test_generate_test_alert(self, mock_get_db, mock_get_jwt_identity):
        """Test generating a test alert."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.user_id
        
        # Create mock DB
        mock_db = MagicMock()
        mock_db.Alerts.insert_one.return_value = MagicMock(inserted_id=ObjectId('5f7d8e9f9f7d8e9f9f7d8e9f'))
        mock_get_db.return_value = mock_db
        
        # Make request
        response = self.client.post(
            '/api/alerts/generate',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        # Verify response data
        self.assertEqual(data['userId'], self.user_id)
        self.assertEqual(data['type'], 'interaction')
        self.assertEqual(data['severity'], 'medium')
        self.assertEqual(data['read'], False)
        self.assertIn('_id', data)
        
        # Verify mock calls
        mock_get_db.assert_called_once()
        mock_db.Alerts.insert_one.assert_called_once()
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.routes.alerts.get_db')
    def test_generate_test_alert_exception(self, mock_get_db, mock_get_jwt_identity):
        """Test error handling when generating a test alert."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.user_id
        mock_get_db.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.post(
            '/api/alerts/generate',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Failed to generate test alert')
        self.assertEqual(data['details'], 'Database error')


if __name__ == '__main__':
    unittest.main()
