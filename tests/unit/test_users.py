import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import datetime
from bson.objectid import ObjectId

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.user import User
from tests.utils import create_mock_mongo_client


class TestUser(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        # Create a mock ObjectId to avoid instantiation issues
        self.mock_object_id = MagicMock()
        self.mock_object_id.__str__.return_value = '507f1f77bcf86cd799439011'
        
        self.test_user_data = {
            '_id': self.mock_object_id,  # Mock ObjectId
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
    @patch('app.models.user.User.validate_email')
    @patch('app.models.user.User.is_email_unique')
    def test_create_user(self, mock_is_email_unique, mock_validate_email, mock_hash_password, mock_get_db):
        """Test creating a new user."""
        # Setup mocks
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = None  # No existing user with same email
        mock_get_db.return_value = mock_db
        mock_hash_password.return_value = 'hashed_password'
        
        # Mock the email validation and uniqueness check to return True
        mock_validate_email.return_value = True
        mock_is_email_unique.return_value = True
        
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
        
        # Verify the validation methods were called correctly
        mock_validate_email.assert_called_once_with('test@example.com')
        mock_is_email_unique.assert_called_once_with('test@example.com')
        
        # Verify the database calls were made correctly
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
        
        # Find the user - pass our mock ObjectId
        user = User.find_by_id(self.mock_object_id)
        
        # Assert the user was found and returned correctly
        self.assertIsNotNone(user)
        self.assertEqual(user.user_id, 'USER123456789')
        self.assertEqual(user.name, 'Test User')
        
        # Verify the mock was called correctly with the mock ObjectId
        mock_db.Users.find_one.assert_called_once_with({'_id': self.mock_object_id, 'deletedAt': None})
    
    @patch('app.models.user.get_db')
    def test_find_by_id_nonexistent_user(self, mock_get_db):
        """Test finding a user by ID when the user doesn't exist."""
        # Setup mock
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = None
        mock_get_db.return_value = mock_db
        
        # Create a mock ObjectId for a nonexistent user
        nonexistent_id = MagicMock()
        nonexistent_id.__str__.return_value = '507f1f77bcf86cd799439099'
        
        # Try to find a nonexistent user with our mock ObjectId
        user = User.find_by_id(nonexistent_id)
        
        # Assert the user was not found
        self.assertIsNone(user)
        
        # Verify the mock was called with the right mock ObjectId
        mock_db.Users.find_one.assert_called_once_with({'_id': nonexistent_id, 'deletedAt': None})


if __name__ == '__main__':
    unittest.main()
