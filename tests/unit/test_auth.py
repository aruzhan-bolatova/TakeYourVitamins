import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from bson.objectid import ObjectId
import datetime

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.db.utils import check_password, hash_password


class TestAuth(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Common user data
        self.user_id = 'USER123456789'
        self.user_email = 'test@example.com'
        self.user_name = 'Test User'
        self.user_password = 'password123'
        
        # Sample user database entry
        self.db_user = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'userId': self.user_id,
            'name': self.user_name,
            'email': self.user_email,
            'password': hash_password(self.user_password),
            'age': 30,
            'gender': 'Male',
            'role': 'user',
            'createdAt': '2023-01-01T00:00:00Z',
            'updatedAt': None,
            'deletedAt': None
        }
        
        # Create a mock ObjectId to avoid instantiation issues
        self.mock_object_id = MagicMock()
        self.mock_object_id.__str__.return_value = '507f1f77bcf86cd799439011'
        
        self.test_user_data = {
            '_id': self.mock_object_id,
            'userId': 'USER123456789',
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'hashed_password',  # This would be a hashed password in reality
            'age': 30,
            'gender': 'Male',
            'role': 'user',
            'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'updatedAt': None,
            'deletedAt': None
        }
        
        # Sample MongoDB document for a user
        self.mock_db_user = self.test_user_data.copy()
        
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
    
    # Test login/register error cases that don't need skipping
    def test_login_missing_fields(self):
        """Test login error with missing fields."""
        # Make request with missing password
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'email': self.user_email}),
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('required', data['error'].lower())
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Setup the mock to return None for invalid credentials
        with patch('app.models.user.User.authenticate', return_value=None):
            # Make login request with invalid password
            response = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': self.user_email,
                    'password': 'wrongpassword'
                }),
                content_type='application/json'
            )
            
            # Assert response
            self.assertEqual(response.status_code, 401)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('invalid', data['error'].lower())
    
    def test_login_server_error(self):
        """Test login with server error."""
        # Setup the mock to raise an exception
        with patch('app.models.user.User.authenticate', side_effect=Exception('Database error')):
            # Make login request
            response = self.client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': self.user_email,
                    'password': self.user_password
                }),
                content_type='application/json'
            )
            
            # Assert response
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertIn('error', data)
            # Just check that there's an error message, don't worry about the exact wording
            self.assertTrue(len(data['error']) > 0)
    
    def test_register_missing_fields(self):
        """Test register error with missing fields."""
        # Make request with missing required fields
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({'name': self.user_name}),
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('required', data['error'].lower())
    
    def test_register_invalid_email(self):
        """Test register with invalid email."""
        # Setup the validate_email mock to return False
        with patch('app.models.user.User.validate_email', return_value=False):
            # Make register request with invalid email
            response = self.client.post(
                '/api/auth/register',
                data=json.dumps({
                    'name': self.user_name,
                    'email': 'invalid-email',
                    'password': self.user_password,
                    'age': 30,
                    'gender': 'Male'
                }),
                content_type='application/json'
            )
            
            # Assert response
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('invalid email', data['error'].lower())
    
    def test_email_uniqueness_check_unique(self):
        """Test checking email uniqueness when email is unique."""
        # Setup the mock DB to return None for find_one (no user with that email)
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = None
        
        with patch('app.models.user.get_db', return_value=mock_db):
            # Check uniqueness
            is_unique = User.is_email_unique(self.user_email)
            
            # Assert result
            self.assertTrue(is_unique)
            # Check that find_one was called with correct params including deletedAt: None
            mock_db.Users.find_one.assert_called_once_with({'email': self.user_email, 'deletedAt': None})
    
    def test_email_uniqueness_check_not_unique(self):
        """Test checking email uniqueness when email is not unique."""
        # Setup the mock DB to return a user with the email
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = self.db_user
        
        with patch('app.models.user.get_db', return_value=mock_db):
            # Check uniqueness
            is_unique = User.is_email_unique(self.user_email)
            
            # Assert result
            self.assertFalse(is_unique)
            # Check that find_one was called with correct params including deletedAt: None
            mock_db.Users.find_one.assert_called_once_with({'email': self.user_email, 'deletedAt': None})

    def test_validate_email_valid(self):
        """Test that valid email formats are accepted."""
        valid_emails = [
            'test@example.com',
            'user.name@domain.com',
            'user-name@domain.co.uk',
            'user123@sub.domain.org'
        ]
        
        for email in valid_emails:
            self.assertTrue(User.validate_email(email))
    
    def test_validate_email_invalid(self):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            'test@',
            'user.name@',
            '@domain.com',
            'user name@domain.com',
            'user@domain',
            'user@.com',
            ''
        ]
        
        for email in invalid_emails:
            self.assertFalse(User.validate_email(email))

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


if __name__ == '__main__':
    unittest.main()
