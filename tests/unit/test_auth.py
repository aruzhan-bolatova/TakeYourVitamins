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
from app.models.token_blacklist import TokenBlacklist


class TestAuth(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Sample user data
        self.test_user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'age': 30,
            'gender': 'Male'
        }
        
        # Mock user object for testing
        self.mock_user = MagicMock()
        self.mock_user.user_id = 'USER123456789'
        self.mock_user.name = self.test_user_data['name']
        self.mock_user.email = self.test_user_data['email']
        self.mock_user.age = self.test_user_data['age']
        self.mock_user.gender = self.test_user_data['gender']
    
    def tearDown(self):
        """Tear down test fixtures after each test method is run."""
        self.app_context.pop()
    
    @patch('app.models.user.User.create')
    def test_register_success(self, mock_create):
        """Test successful user registration."""
        # Setup mock
        mock_create.return_value = self.mock_user
        
        # Make request
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], 'User registered successfully')
        self.assertEqual(data['userId'], 'USER123456789')
        self.assertIn('access_token', data)
        
        # Verify mock calls
        mock_create.assert_called_once_with(
            name=self.test_user_data['name'],
            email=self.test_user_data['email'],
            password=self.test_user_data['password'],
            age=self.test_user_data['age'],
            gender=self.test_user_data['gender']
        )
    
    def test_register_missing_fields(self):
        """Test registration with missing fields."""
        # Make request with missing password
        incomplete_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'age': 30,
            'gender': 'Male'
        }
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Missing required field: password')
    
    @patch('app.models.user.User.create')
    def test_register_email_exists(self, mock_create):
        """Test registration with an existing email."""
        # Setup mock to raise ValueError
        mock_create.side_effect = ValueError('Email already exists')
        
        # Make request
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Email already exists')
    
    @patch('app.models.user.User.create')
    def test_register_server_error(self, mock_create):
        """Test registration with server error."""
        # Setup mock to raise a generic exception
        mock_create.side_effect = Exception('Database connection error')
        
        # Make request
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['error'], 'Failed to register user')
        self.assertIn('Database connection error', data['details'])
    
    def test_register_not_json(self):
        """Test registration with non-JSON content."""
        # Make request with non-JSON content
        response = self.client.post(
            '/api/auth/register',
            data="This is not JSON",
            content_type='text/plain'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    @patch('app.models.user.User.authenticate')
    def test_login_success(self, mock_authenticate):
        """Test successful login."""
        # Setup mock
        mock_authenticate.return_value = self.mock_user
        
        # Make request
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({
                'email': self.test_user_data['email'],
                'password': self.test_user_data['password']
            }),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Login successful')
        self.assertEqual(data['userId'], 'USER123456789')
        self.assertIn('access_token', data)
        
        # Verify mock calls
        mock_authenticate.assert_called_once_with(
            self.test_user_data['email'],
            self.test_user_data['password']
        )
    
    @patch('app.models.user.User.authenticate')
    def test_login_invalid_credentials(self, mock_authenticate):
        """Test login with invalid credentials."""
        # Setup mock to return None (authentication failure)
        mock_authenticate.return_value = None
        
        # Make request
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({
                'email': self.test_user_data['email'],
                'password': 'wrong_password'
            }),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['error'], 'Invalid email or password')
    
    def test_login_missing_fields(self):
        """Test login with missing fields."""
        # Make request with missing password
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'email': self.test_user_data['email']}),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Email and password are required')
    
    def test_login_not_json(self):
        """Test login with non-JSON content."""
        # Make request with non-JSON content
        response = self.client.post(
            '/api/auth/login',
            data="This is not JSON",
            content_type='text/plain'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    @patch('app.models.token_blacklist.TokenBlacklist.add_to_blacklist')
    @patch('flask_jwt_extended.utils.get_jwt')
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    def test_logout_success(self, mock_get_jwt_identity, mock_get_jwt, mock_add_to_blacklist):
        """Test successful logout."""
        # Set up mocks
        mock_get_jwt_identity.return_value = 'USER123456789'
        mock_get_jwt.return_value = {
            'jti': 'test_jti',
            'exp': datetime.datetime.now(tz=datetime.timezone.utc).timestamp() + 3600
        }
        
        # Login to get a token
        with patch('app.models.user.User.authenticate', return_value=self.mock_user):
            login_response = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': self.test_user_data['email'],
                    'password': self.test_user_data['password']
                }),
                content_type='application/json'
            )
            
            token = json.loads(login_response.data)['access_token']
        
        # Make logout request
        response = self.client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Successfully logged out')
        
        # Verify the token was added to the blacklist
        mock_add_to_blacklist.assert_called_once()
    
    @patch('app.models.token_blacklist.TokenBlacklist.add_to_blacklist')
    @patch('flask_jwt_extended.utils.get_jwt')
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    def test_logout_exception_handling(self, mock_get_jwt_identity, mock_get_jwt, mock_add_to_blacklist):
        """Test logout with exception in TokenBlacklist."""
        # Set up mocks
        mock_get_jwt_identity.return_value = 'USER123456789'
        mock_get_jwt.return_value = {
            'jti': 'test_jti',
            'exp': datetime.datetime.now(tz=datetime.timezone.utc).timestamp() + 3600
        }
        mock_add_to_blacklist.side_effect = Exception('Database error')
        
        # Login to get a token
        with patch('app.models.user.User.authenticate', return_value=self.mock_user):
            login_response = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': self.test_user_data['email'],
                    'password': self.test_user_data['password']
                }),
                content_type='application/json'
            )
            
            token = json.loads(login_response.data)['access_token']
        
        # Make logout request
        response = self.client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Assert response - should still return success even if there's an error
        # with the blacklist (best practice not to leak internal errors)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Successfully logged out')
    
    @patch('app.models.user.User.find_by_id')
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    def test_get_current_user(self, mock_get_jwt_identity, mock_find_by_id):
        """Test retrieving the current user's information."""
        # Set up mocks
        mock_get_jwt_identity.return_value = 'USER123456789'
        mock_find_by_id.return_value = self.mock_user
        
        # Login to get a token
        with patch('app.models.user.User.authenticate', return_value=self.mock_user):
            login_response = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': self.test_user_data['email'],
                    'password': self.test_user_data['password']
                }),
                content_type='application/json'
            )
            
            token = json.loads(login_response.data)['access_token']
        
        # Make request to get current user
        response = self.client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['userId'], 'USER123456789')
        self.assertEqual(data['name'], self.test_user_data['name'])
        self.assertEqual(data['email'], self.test_user_data['email'])
        
        # Verify mock calls
        mock_find_by_id.assert_called_once_with('USER123456789')
    
    @patch('app.models.user.User.find_by_id')
    @patch('flask_jwt_extended.utils.get_jwt_identity')
    def test_get_current_user_not_found(self, mock_get_jwt_identity, mock_find_by_id):
        """Test retrieving a user that doesn't exist anymore."""
        # Set up mocks
        mock_get_jwt_identity.return_value = 'NONEXISTENT_USER'
        mock_find_by_id.return_value = None
        
        # Login to get a token
        with patch('app.models.user.User.authenticate', return_value=self.mock_user):
            login_response = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': self.test_user_data['email'],
                    'password': self.test_user_data['password']
                }),
                content_type='application/json'
            )
            
            token = json.loads(login_response.data)['access_token']
        
        # Make request to get current user
        response = self.client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'User not found')


if __name__ == '__main__':
    unittest.main()
