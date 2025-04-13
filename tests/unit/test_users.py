import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import datetime

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.user import User
from tests.utils import create_mock_mongo_client


class TestUser(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        self.test_user_data = {
            'userId': 'USER123456789',
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'hashed_password',  # This would be a hashed password in reality
            'age': 30,
            'gender': 'Male',
            'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'updatedAt': None,
            'deletedAt': None
        }
        
        # Sample MongoDB document for a user
        self.mock_db_user = self.test_user_data.copy()
    
    @patch('app.models.user.get_db')
    @patch('app.models.user.hash_password')
    def test_create_user(self, mock_hash_password, mock_get_db):
        """Test creating a new user."""
        # Setup mocks
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = None  # No existing user with same email
        mock_get_db.return_value = mock_db
        mock_hash_password.return_value = 'hashed_password'
        
        # Call the create method
        user = User.create(
            name='Test User',
            email='test@example.com',
            password='password123',
            age=30,
            gender='Male'
        )
        
        # Assert the user was created with the correct data
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.age, 30)
        self.assertEqual(user.gender, 'Male')
        
        # Verify the database was called correctly
        mock_db.Users.find_one.assert_called_once_with({'email': 'test@example.com'})
        mock_db.Users.insert_one.assert_called_once()
        mock_hash_password.assert_called_once_with('password123')
    
    @patch('app.models.user.get_db')
    def test_create_user_email_exists(self, mock_get_db):
        """Test that creating a user with an existing email raises an error."""
        # Setup mock to return an existing user
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = self.mock_db_user
        mock_get_db.return_value = mock_db
        
        # Test that creating a user with existing email raises ValueError
        with self.assertRaises(ValueError):
            User.create(
                name='Another User',
                email='test@example.com',  # Same email as existing user
                password='password123',
                age=25,
                gender='Female'
            )
    
    @patch('app.models.user.get_db')
    @patch('app.models.user.check_password')
    def test_authenticate_valid_credentials(self, mock_check_password, mock_get_db):
        """Test authenticating a user with valid credentials."""
        # Setup mocks
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = self.mock_db_user
        mock_get_db.return_value = mock_db
        mock_check_password.return_value = True
        
        # Authenticate the user
        user = User.authenticate('test@example.com', 'password123')
        
        # Assert the user was authenticated and returned correctly
        self.assertIsNotNone(user)
        self.assertEqual(user.user_id, 'USER123456789')
        self.assertEqual(user.email, 'test@example.com')
        
        # Verify the mocks were called correctly - now includes deletedAt: None
        mock_db.Users.find_one.assert_called_once_with({'email': 'test@example.com', 'deletedAt': None})
        mock_check_password.assert_called_once_with('password123', 'hashed_password')
    
    @patch('app.models.user.get_db')
    @patch('app.models.user.check_password')
    def test_authenticate_invalid_credentials(self, mock_check_password, mock_get_db):
        """Test authenticating a user with invalid credentials."""
        # Setup mocks
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = self.mock_db_user
        mock_get_db.return_value = mock_db
        mock_check_password.return_value = False  # Password doesn't match
        
        # Try to authenticate with wrong password
        user = User.authenticate('test@example.com', 'wrong_password')
        
        # Assert authentication failed
        self.assertIsNone(user)
    
    @patch('app.models.user.get_db')
    def test_find_by_id_existing_user(self, mock_get_db):
        """Test finding a user by ID when the user exists."""
        # Setup mock
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = self.mock_db_user
        mock_get_db.return_value = mock_db
        
        # Find the user
        user = User.find_by_id('USER123456789')
        
        # Assert the user was found and returned correctly
        self.assertIsNotNone(user)
        self.assertEqual(user.user_id, 'USER123456789')
        self.assertEqual(user.name, 'Test User')
        
        # Verify the mock was called correctly - now includes deletedAt: None
        mock_db.Users.find_one.assert_called_once_with({'userId': 'USER123456789', 'deletedAt': None})
    
    @patch('app.models.user.get_db')
    def test_find_by_id_nonexistent_user(self, mock_get_db):
        """Test finding a user by ID when the user doesn't exist."""
        # Setup mock
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = None
        mock_get_db.return_value = mock_db
        
        # Try to find a nonexistent user
        user = User.find_by_id('NONEXISTENT_USER')
        
        # Assert the user was not found
        self.assertIsNone(user)


class TestUserRoutes(unittest.TestCase):
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
            'role': 'user',
            'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'updatedAt': None,
            'deletedAt': None
        }
        
        # Admin user data
        self.admin_user_data = {
            'userId': 'ADMIN123456789',
            'name': 'Admin User',
            'email': 'admin@example.com',
            'password': 'hashed_password',
            'age': 35,
            'gender': 'Female',
            'role': 'admin',
            'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'updatedAt': None,
            'deletedAt': None
        }

        # Create mock user objects
        self.mock_user = MagicMock()
        self.mock_user.user_id = self.test_user_data['userId']
        self.mock_user.name = self.test_user_data['name']
        self.mock_user.email = self.test_user_data['email']
        self.mock_user.age = self.test_user_data['age']
        self.mock_user.gender = self.test_user_data['gender']
        self.mock_user.role = self.test_user_data['role']
        
        self.mock_admin = MagicMock()
        self.mock_admin.user_id = self.admin_user_data['userId']
        self.mock_admin.name = self.admin_user_data['name']
        self.mock_admin.email = self.admin_user_data['email']
        self.mock_admin.age = self.admin_user_data['age']
        self.mock_admin.gender = self.admin_user_data['gender']
        self.mock_admin.role = self.admin_user_data['role']
    
    def tearDown(self):
        """Tear down test fixtures after each test method is run."""
        self.app_context.pop()
    
    def get_auth_headers(self, user_id):
        """Helper to get authorization headers with JWT token."""
        with patch('app.models.user.User.authenticate', return_value=self.mock_user if user_id == self.test_user_data['userId'] else self.mock_admin):
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
    def test_get_current_user_profile(self, mock_find_by_id, mock_get_jwt_identity):
        """Test getting the current user's profile."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.test_user_data['userId']
        mock_find_by_id.return_value = self.mock_user
        
        # Make request
        response = self.client.get(
            '/api/users/',
            headers=self.get_auth_headers(self.test_user_data['userId'])
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['userId'], self.test_user_data['userId'])
        self.assertEqual(data['name'], self.test_user_data['name'])
        self.assertEqual(data['email'], self.test_user_data['email'])
        
        # Verify mock calls
        mock_find_by_id.assert_called_once_with(self.test_user_data['userId'])
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.models.user.User.find_by_id')
    def test_get_user_profile(self, mock_find_by_id, mock_get_jwt_identity):
        """Test getting a specific user's profile."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.test_user_data['userId']
        mock_find_by_id.side_effect = lambda user_id, **kwargs: self.mock_user if user_id == self.test_user_data['userId'] else None
        
        # Make request
        response = self.client.get(
            f'/api/users/{self.test_user_data["userId"]}',
            headers=self.get_auth_headers(self.test_user_data['userId'])
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['userId'], self.test_user_data['userId'])
        self.assertEqual(data['name'], self.test_user_data['name'])
        
        # Verify mock was called
        self.assertTrue(mock_find_by_id.called)
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.models.user.User.find_by_id')
    def test_get_other_user_profile_unauthorized(self, mock_find_by_id, mock_get_jwt_identity):
        """Test that a user can't access another user's profile."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.test_user_data['userId']
        mock_find_by_id.side_effect = lambda user_id, **kwargs: self.mock_user if user_id == self.test_user_data['userId'] else None
        
        # Make request for a different user
        other_user_id = 'OTHER123456789'
        response = self.client.get(
            f'/api/users/{other_user_id}',
            headers=self.get_auth_headers(self.test_user_data['userId'])
        )
        
        # Assert response (should be forbidden)
        self.assertEqual(response.status_code, 403)
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.models.user.User.find_by_id')
    @patch('app.models.user.User.update')
    def test_update_user_profile(self, mock_update, mock_find_by_id, mock_get_jwt_identity):
        """Test updating a user's profile."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.test_user_data['userId']
        mock_find_by_id.return_value = self.mock_user
        
        # Create an updated user mock
        updated_user = MagicMock()
        updated_user.user_id = self.test_user_data['userId']
        updated_user.name = 'Updated Name'
        updated_user.email = self.test_user_data['email']
        updated_user.age = 31
        updated_user.gender = self.test_user_data['gender']
        updated_user.role = self.test_user_data['role']
        
        mock_update.return_value = updated_user
        
        # Make request
        update_data = {
            'name': 'Updated Name',
            'age': 31
        }
        response = self.client.put(
            f'/api/users/{self.test_user_data["userId"]}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.get_auth_headers(self.test_user_data['userId'])
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'User updated successfully')
        self.assertEqual(data['name'], 'Updated Name')
        self.assertEqual(data['age'], 31)
        
        # Verify mock calls
        mock_update.assert_called_once_with(self.test_user_data['userId'], update_data)
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.models.user.User.find_by_id')
    @patch('app.models.user.User.delete')
    def test_delete_user(self, mock_delete, mock_find_by_id, mock_get_jwt_identity):
        """Test deleting a user."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.test_user_data['userId']
        mock_find_by_id.return_value = self.mock_user
        
        # Create a deleted user mock
        deleted_user = MagicMock()
        deleted_user.user_id = self.test_user_data['userId']
        deleted_user.deleted_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        mock_delete.return_value = deleted_user
        
        # Make request
        response = self.client.delete(
            f'/api/users/{self.test_user_data["userId"]}',
            headers=self.get_auth_headers(self.test_user_data['userId'])
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'User deleted successfully')
        self.assertEqual(data['userId'], self.test_user_data['userId'])
        
        # Verify mock calls
        mock_delete.assert_called_once_with(self.test_user_data['userId'])
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.models.user.User.find_by_id')
    @patch('app.routes.users.get_db')
    def test_admin_get_all_users(self, mock_get_db, mock_find_by_id, mock_get_jwt_identity):
        """Test the admin endpoint to get all users."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.admin_user_data['userId']
        mock_find_by_id.return_value = self.mock_admin
        
        # Create fake user data
        user1 = {
            "userId": "USER1",
            "name": "User One",
            "email": "user1@example.com",
            "age": 30,
            "gender": "Male",
            "role": "user",
            "createdAt": "2023-01-01T00:00:00Z"
        }
        
        user2 = {
            "userId": "USER2",
            "name": "User Two",
            "email": "user2@example.com",
            "age": 25,
            "gender": "Female",
            "role": "user", 
            "createdAt": "2023-01-02T00:00:00Z"
        }
        
        # Create a function to replace db.Users.find
        def mock_find(query):
            # This function will replace db.Users.find
            # It should return a list-like object that when converted to a list contains our test users
            class MockCursor:
                def __iter__(self):
                    return iter([user1, user2])
            return MockCursor()
        
        # Set up our mock database
        mock_db_instance = MagicMock()
        mock_db_instance.Users.find = mock_find
        mock_get_db.return_value = mock_db_instance
        
        # Make request
        response = self.client.get(
            '/api/users/admin/all',
            headers=self.get_auth_headers(self.admin_user_data['userId'])
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', data)
        
        # Check we have the right number of users
        self.assertEqual(len(data['users']), 2)
        
        # Check the user details are correct
        user_ids = [user['userId'] for user in data['users']]
        self.assertIn("USER1", user_ids)
        self.assertIn("USER2", user_ids)
    
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    @patch('app.models.user.User.find_by_id')
    def test_non_admin_cannot_access_admin_routes(self, mock_find_by_id, mock_get_jwt_identity):
        """Test that non-admin users cannot access admin routes."""
        # Setup mocks
        mock_get_jwt_identity.return_value = self.test_user_data['userId']
        mock_find_by_id.return_value = self.mock_user  # Regular user, not admin
        
        # Make request to admin route
        response = self.client.get(
            '/api/users/admin/all',
            headers=self.get_auth_headers(self.test_user_data['userId'])
        )
        
        # Assert response (should be forbidden)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Admin privileges required')


if __name__ == '__main__':
    unittest.main()
