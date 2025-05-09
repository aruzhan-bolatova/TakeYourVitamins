import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from flask_jwt_extended import create_access_token, JWTManager, get_jwt
import sys
import os
import json
from datetime import datetime, timedelta, timezone

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.routes.auth import bp as auth_bp

class TestAuthRoutes(unittest.TestCase):

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

        # Register blueprint
        self.app.register_blueprint(auth_bp)

        # Sample user data
        self.user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'Password123',
            'age': 30,
            'gender': 'male'
        }

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    # Register Tests
    @patch('app.routes.auth.User.create')
    @patch('app.routes.auth.create_access_token')
    def test_register_success(self, mock_create_token, mock_create_user):
        """Test successful user registration."""
        # Configure mocks
        mock_user = MagicMock()
        mock_user._id = '123456789012345678901234'
        mock_create_user.return_value = mock_user
        mock_create_token.return_value = 'fake-token'

        # Make request
        response = self.client.post(
            '/api/auth/register',
            json=self.user_data
        )
        
        # Assert response
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User registered successfully')
        self.assertIn('access_token', data)
        self.assertEqual(data['access_token'], 'fake-token')
        
        # Verify create_user was called with correct arguments
        mock_create_user.assert_called_once_with(
            name=self.user_data['name'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            age=self.user_data['age'],
            gender=self.user_data['gender']
        )

    def test_register_missing_json(self):
        """Test registration with missing JSON."""
        # Make request without JSON
        response = self.client.post('/api/auth/register')
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Missing JSON in request')

    def test_register_invalid_json(self):
        """Test registration with invalid JSON."""
        # Make request with invalid JSON content type but no actual JSON
        response = self.client.post(
            '/api/auth/register',
            data='not valid json',
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid JSON format')

    def test_register_missing_fields(self):
        """Test registration with missing required fields."""
        # Make request with missing gender field
        incomplete_data = self.user_data.copy()
        del incomplete_data['gender']
        
        response = self.client.post(
            '/api/auth/register',
            json=incomplete_data
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Missing required field', data['error'])

    @patch('app.routes.auth.User.create')
    def test_register_value_error(self, mock_create_user):
        """Test registration with ValueError from User.create."""
        # Configure mock
        mock_create_user.side_effect = ValueError('Email is invalid')

        # Make request
        response = self.client.post(
            '/api/auth/register',
            json=self.user_data
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Email is invalid')

    @patch('app.routes.auth.User.create')
    def test_register_exception(self, mock_create_user):
        """Test registration with unexpected exception."""
        # Configure mock
        mock_create_user.side_effect = Exception('Database error')

        # Make request
        response = self.client.post(
            '/api/auth/register',
            json=self.user_data
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Failed to register user')
        self.assertIn('details', data)

    # Login Tests
    @patch('app.routes.auth.User.authenticate')
    @patch('app.routes.auth.create_access_token')
    def test_login_success(self, mock_create_token, mock_authenticate):
        """Test successful login."""
        # Configure mocks
        mock_user = MagicMock()
        mock_user._id = '123456789012345678901234'
        mock_authenticate.return_value = mock_user
        mock_create_token.return_value = 'fake-token'

        # Make request
        response = self.client.post(
            '/api/auth/login',
            json={
                'email': self.user_data['email'],
                'password': self.user_data['password']
            }
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Login successful')
        self.assertIn('access_token', data)
        self.assertEqual(data['access_token'], 'fake-token')
        
        # Verify authenticate was called with correct arguments
        mock_authenticate.assert_called_once_with(
            self.user_data['email'],
            self.user_data['password']
        )

    def test_login_missing_json(self):
        """Test login with missing JSON."""
        # Make request without JSON
        response = self.client.post('/api/auth/login')
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Missing JSON in request')

    def test_login_invalid_json(self):
        """Test login with invalid JSON."""
        # Make request with invalid JSON content type but no actual JSON
        response = self.client.post(
            '/api/auth/login',
            data='not valid json',
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid JSON format')

    def test_login_missing_fields(self):
        """Test login with missing required fields."""
        # Make request with missing password field
        response = self.client.post(
            '/api/auth/login',
            json={'email': self.user_data['email']}
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Email and password are required')

    @patch('app.routes.auth.User.authenticate')
    def test_login_invalid_credentials(self, mock_authenticate):
        """Test login with invalid credentials."""
        # Configure mock
        mock_authenticate.return_value = None

        # Make request
        response = self.client.post(
            '/api/auth/login',
            json={
                'email': self.user_data['email'],
                'password': 'wrong-password'
            }
        )
        
        # Assert response
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid email or password')

    # Logout Tests
    @patch('app.routes.auth.TokenBlacklist.add_to_blacklist')
    def test_logout_success(self, mock_add_to_blacklist):
        """Test successful logout."""
        # Create access token
        with self.app.test_request_context():
            access_token = create_access_token(identity='123456789012345678901234')
            
        # Make request with token
        response = self.client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Successfully logged out')
        
        # Verify add_to_blacklist was called
        mock_add_to_blacklist.assert_called_once()

    @patch('app.routes.auth.TokenBlacklist.add_to_blacklist')
    def test_logout_exception(self, mock_add_to_blacklist):
        """Test logout with exception in blacklisting."""
        # Configure mock
        mock_add_to_blacklist.side_effect = Exception('Database error')

        # Create access token
        with self.app.test_request_context():
            access_token = create_access_token(identity='123456789012345678901234')
            
        # Make request with token
        response = self.client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # Assert response is still successful (fails gracefully)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Successfully logged out')

    def test_logout_no_token(self):
        """Test logout without token."""
        # Make request without token
        response = self.client.post('/api/auth/logout')
        
        # Assert response
        self.assertEqual(response.status_code, 401)

    # Get Current User Tests
    @patch('app.routes.auth.User.find_by_id')
    def test_get_current_user_success(self, mock_find_by_id):
        """Test getting current user successfully."""
        # Configure mock
        mock_user = MagicMock()
        mock_user._id = '123456789012345678901234'
        mock_user.user_id = 'user123'
        mock_user.name = 'Test User'
        mock_user.email = 'test@example.com'
        mock_user.age = 30
        mock_user.gender = 'male'
        mock_find_by_id.return_value = mock_user

        # Create access token
        with self.app.test_request_context():
            access_token = create_access_token(identity='123456789012345678901234')
            
        # Make request with token
        response = self.client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('_id', data)
        self.assertEqual(data['_id'], '123456789012345678901234')
        self.assertEqual(data['name'], 'Test User')
        self.assertEqual(data['email'], 'test@example.com')

    @patch('app.routes.auth.User.find_by_id')
    def test_get_current_user_not_found(self, mock_find_by_id):
        """Test getting current user when user is not found."""
        # Configure mock
        mock_find_by_id.return_value = None

        # Create access token
        with self.app.test_request_context():
            access_token = create_access_token(identity='123456789012345678901234')
            
        # Make request with token
        response = self.client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')

    def test_get_current_user_no_token(self):
        """Test getting current user without token."""
        # Make request without token
        response = self.client.get('/api/auth/me')
        
        # Assert response
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main() 