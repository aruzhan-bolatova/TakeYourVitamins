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
from app.models.user import User
from app.routes.users import bp as users_bp

class TestUsersRoutes(unittest.TestCase):

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
        self.other_user_id = str(ObjectId())
        
        # Create access tokens
        self.access_token = create_access_token(identity=self.user_id)
        self.admin_access_token = create_access_token(identity=self.admin_user_id)
        self.headers = {'Authorization': f'Bearer {self.access_token}'}
        self.admin_headers = {'Authorization': f'Bearer {self.admin_access_token}'}

        # Register blueprint
        self.app.register_blueprint(users_bp)

        # Create dummy user data
        self.user_data = {
            "_id": self.user_id,
            "userId": "user123",
            "name": "Test User",
            "email": "test@example.com",
            "age": 30,
            "gender": "male",
            "role": "user"
        }

        # Mock auth middleware to bypass access checks for simplicity in tests
        self.auth_patcher = patch('app.routes.users.check_user_access', lambda f: f)
        self.auth_mock = self.auth_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.auth_patcher.stop()
        self.app_context.pop()

    @patch('app.routes.users.User.find_by_id')
    def test_get_current_user_profile_success(self, mock_find_by_id):
        """Test getting current user profile successfully."""
        # Configure mock
        mock_user = MagicMock()
        mock_user.to_dict.return_value = self.user_data
        mock_find_by_id.return_value = mock_user

        # Make request
        response = self.client.get(
            '/api/users/',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, self.user_data)
        
        # Verify find_by_id was called with correct arguments
        mock_find_by_id.assert_called_once()

    @patch('app.routes.users.User.find_by_id')
    def test_get_current_user_profile_not_found(self, mock_find_by_id):
        """Test getting current user profile when user is not found."""
        # Configure mock
        mock_find_by_id.return_value = None

        # Make request
        response = self.client.get(
            '/api/users/',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')

    @patch('app.routes.users.User.find_by_id')
    def test_get_user_profile_success(self, mock_find_by_id):
        """Test getting a specific user profile successfully."""
        # Configure mock
        mock_user = MagicMock()
        mock_user.to_dict.return_value = self.user_data
        mock_find_by_id.return_value = mock_user

        # Make request
        response = self.client.get(
            f'/api/users/{self.user_id}',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, self.user_data)
        
        # Verify find_by_id was called (may be called multiple times due to auth middleware)
        mock_find_by_id.assert_called()

    def test_get_user_profile_invalid_id(self):
        """Test getting a user profile with an invalid ID."""
        # Make request with invalid ID
        response = self.client.get(
            '/api/users/invalid-id',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch('app.routes.users.User.find_by_id')
    def test_get_user_profile_not_found(self, mock_find_by_id):
        """Test getting a user profile when user is not found."""
        # Configure mock
        mock_find_by_id.return_value = None

        # Make request
        response = self.client.get(
            f'/api/users/{self.user_id}',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')

    @patch('app.routes.users.User.find_by_id')
    def test_get_user_profile_server_error(self, mock_find_by_id):
        """Test getting a user profile when a server error occurs."""
        # Configure mock to raise an exception
        mock_find_by_id.side_effect = Exception("Database error")

        # Make request
        response = self.client.get(
            f'/api/users/{self.user_id}',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Internal Server Error')

    @patch('app.routes.users.User.update')
    def test_update_user_profile_success(self, mock_update):
        """Test updating a user profile successfully."""
        # Configure mock
        updated_user = MagicMock()
        updated_user.user_id = "user123"
        updated_user.name = "Updated Name"
        updated_user.email = "test@example.com"
        updated_user.age = 31
        updated_user.gender = "male"
        updated_user.role = "user"
        mock_update.return_value = updated_user

        update_data = {"name": "Updated Name", "age": 31}

        # Make request
        response = self.client.put(
            f'/api/users/{self.user_id}',
            json=update_data,
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User updated successfully')
        self.assertEqual(data['name'], "Updated Name")
        self.assertEqual(data['age'], 31)
        
        # Verify update was called with correct arguments
        mock_update.assert_called_once_with(ObjectId(self.user_id), update_data)

    def test_update_user_profile_missing_data(self):
        """Test updating a user profile with missing data."""
        # Make request without json data
        response = self.client.put(
            f'/api/users/{self.user_id}',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No update data provided')

    def test_update_user_profile_invalid_id(self):
        """Test updating a user profile with an invalid ID."""
        # Make request with invalid ID
        response = self.client.put(
            '/api/users/invalid-id',
            json={"name": "Updated Name"},
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch('app.routes.users.User.update')
    def test_update_user_profile_not_found(self, mock_update):
        """Test updating a user profile that doesn't exist."""
        # Configure mock
        mock_update.return_value = None

        # Make request
        response = self.client.put(
            f'/api/users/{self.user_id}',
            json={"name": "Updated Name"},
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')

    @patch('app.routes.users.User.update')
    def test_update_user_profile_validation_error(self, mock_update):
        """Test updating a user profile with validation error."""
        # Configure mock
        mock_update.side_effect = ValueError("Invalid email format")

        # Make request
        response = self.client.put(
            f'/api/users/{self.user_id}',
            json={"email": "invalid-email"},
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid email format')

    @patch('app.routes.users.User.delete')
    def test_delete_user_success(self, mock_delete):
        """Test deleting a user successfully."""
        # Configure mock
        mock_deleted_user = MagicMock()
        mock_deleted_user._id = ObjectId(self.user_id)
        mock_delete.return_value = mock_deleted_user

        # Make request
        response = self.client.delete(
            f'/api/users/{self.user_id}',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User deleted successfully')
        self.assertIn('_id', data)
        self.assertEqual(data['_id'], self.user_id)
        
        # Verify delete was called with correct arguments
        mock_delete.assert_called_once_with(ObjectId(self.user_id))

    def test_delete_user_invalid_id(self):
        """Test deleting a user with an invalid ID."""
        # Make request with invalid ID
        response = self.client.delete(
            '/api/users/invalid-id',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch('app.routes.users.User.delete')
    def test_delete_user_not_found(self, mock_delete):
        """Test deleting a user that doesn't exist."""
        # Configure mock
        mock_delete.return_value = None

        # Make request
        response = self.client.delete(
            f'/api/users/{self.user_id}',
            headers=self.headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')

    @patch('app.routes.users.get_db')
    def test_get_all_users_success(self, mock_get_db):
        """Test getting all users successfully."""
        # Configure mock
        mock_db = MagicMock()
        mock_users_collection = MagicMock()
        mock_db.Users = mock_users_collection
        mock_get_db.return_value = mock_db
        
        # Mock the find method to return a list of users
        user1 = {
            "_id": ObjectId(self.user_id),
            "userId": "user123",
            "name": "Test User",
            "email": "test@example.com",
            "age": 30,
            "gender": "male",
            "role": "user",
            "createdAt": "2023-01-01T00:00:00"
        }
        user2 = {
            "_id": ObjectId(self.admin_user_id),
            "userId": "admin123",
            "name": "Admin User",
            "email": "admin@example.com",
            "age": 35,
            "gender": "female",
            "role": "admin",
            "createdAt": "2023-01-02T00:00:00"
        }
        mock_users_collection.find.return_value = [user1, user2]

        # Make request
        response = self.client.get(
            '/api/users/admin/all',
            headers=self.admin_headers
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('users', data)
        self.assertEqual(len(data['users']), 2)
        
        # Verify users were formatted correctly
        self.assertEqual(data['users'][0]['_id'], self.user_id)
        self.assertEqual(data['users'][0]['name'], "Test User")
        self.assertEqual(data['users'][1]['_id'], self.admin_user_id)
        self.assertEqual(data['users'][1]['role'], "admin")
        
        # Verify find was called with correct arguments
        mock_users_collection.find.assert_called_once_with({'deletedAt': None})

if __name__ == '__main__':
    unittest.main() 