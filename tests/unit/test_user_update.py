import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.user import User


class TestUserProfileUpdate(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Sample user data
        self.test_user_data = {
            'userId': 'USER123456789',
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'hashed_password',
            'age': 30,
            'gender': 'Male',
            'role': 'user'
        }
        
        # Create mock user
        self.mock_user = MagicMock()
        self.mock_user.user_id = self.test_user_data['userId']
        self.mock_user.name = self.test_user_data['name']
        self.mock_user.email = self.test_user_data['email']
        self.mock_user.age = self.test_user_data['age']
        self.mock_user.gender = self.test_user_data['gender']
        self.mock_user.role = self.test_user_data['role']
    
    def tearDown(self):
        """Tear down test fixtures after each test method is run."""
        self.app_context.pop()
    
    def get_auth_headers(self):
        """Helper to get authorization headers with JWT token."""
        with patch('app.models.user.User.authenticate', return_value=self.mock_user):
            # Login to get token
            login_data = {'email': 'test@example.com', 'password': 'password123'}
            response = self.client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            token = json.loads(response.data)['access_token']
            return {'Authorization': f'Bearer {token}'}
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.models.user.User.find_by_id')
    @patch('app.models.user.User.update')
    def test_update_profile_success(self, mock_update, mock_find_by_id, mock_get_jwt_identity):
        """Test successful profile update."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.test_user_data['userId']
        mock_find_by_id.return_value = self.mock_user
        
        # Create updated user mock
        updated_user = MagicMock()
        updated_user.user_id = self.test_user_data['userId']
        updated_user.name = 'Updated Name'
        updated_user.email = 'updated@example.com'
        updated_user.age = 31
        updated_user.gender = self.test_user_data['gender']
        updated_user.role = self.test_user_data['role']
        
        mock_update.return_value = updated_user
        
        # Make request
        update_data = {
            'name': 'Updated Name',
            'email': 'updated@example.com',
            'age': 31
        }
        response = self.client.put(
            f'/api/users/{self.test_user_data["userId"]}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'User updated successfully')
        self.assertEqual(data['name'], 'Updated Name')
        self.assertEqual(data['email'], 'updated@example.com')
        self.assertEqual(data['age'], 31)
        
        # Verify mock calls
        mock_update.assert_called_once_with(self.test_user_data['userId'], update_data)
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.models.user.User.find_by_id')
    @patch('app.models.user.User.update')
    def test_update_profile_invalid_email(self, mock_update, mock_find_by_id, mock_get_jwt_identity):
        """Test profile update with invalid email format."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.test_user_data['userId']
        mock_find_by_id.return_value = self.mock_user
        
        # Mock update to raise ValueError for invalid email
        mock_update.side_effect = ValueError('Invalid email format')
        
        # Make request with invalid email
        update_data = {
            'name': 'Updated Name',
            'email': 'invalid-email',  # Invalid email format
            'age': 31
        }
        response = self.client.put(
            f'/api/users/{self.test_user_data["userId"]}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Invalid email format')
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.models.user.User.find_by_id')
    @patch('app.models.user.User.update')
    def test_update_profile_duplicate_email(self, mock_update, mock_find_by_id, mock_get_jwt_identity):
        """Test profile update with email that already exists."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.test_user_data['userId']
        mock_find_by_id.return_value = self.mock_user
        
        # Mock update to raise ValueError for duplicate email
        mock_update.side_effect = ValueError('Email already exists')
        
        # Make request with duplicate email
        update_data = {
            'name': 'Updated Name',
            'email': 'existing@example.com',  # Email that already exists
            'age': 31
        }
        response = self.client.put(
            f'/api/users/{self.test_user_data["userId"]}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Email already exists')
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.models.user.User.find_by_id')
    def test_update_profile_user_not_found(self, mock_find_by_id, mock_get_jwt_identity):
        """Test profile update for non-existent user."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.test_user_data['userId']
        mock_find_by_id.return_value = None  # User not found
        
        # Make request
        update_data = {
            'name': 'Updated Name',
            'age': 31
        }
        response = self.client.put(
            f'/api/users/NONEXISTENT',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.get_auth_headers()
        )
        
        # Assert response
        self.assertEqual(response.status_code, 403)  # Access denied because user doesn't exist


if __name__ == '__main__':
    unittest.main() 