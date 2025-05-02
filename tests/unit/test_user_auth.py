import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from bson.objectid import ObjectId
import datetime

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.models.user import User


class TestUserAuth(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
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
        
        # Verify the mocks were called correctly
        mock_db.Users.find_one.assert_called_once_with({'email': 'test@example.com', 'deletedAt': None})
        mock_check_password.assert_called_once_with('password123', 'hashed_password')
    
    @patch('app.models.user.get_db')
    @patch('app.models.user.check_password')
    def test_authenticate_invalid_password(self, mock_check_password, mock_get_db):
        """Test authenticating a user with invalid password."""
        # Setup mocks
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = self.mock_db_user
        mock_get_db.return_value = mock_db
        mock_check_password.return_value = False  # Password doesn't match
        
        # Try to authenticate with wrong password
        user = User.authenticate('test@example.com', 'wrong_password')
        
        # Assert authentication failed
        self.assertIsNone(user)
        
        # Verify the mocks were called correctly
        mock_db.Users.find_one.assert_called_once_with({'email': 'test@example.com', 'deletedAt': None})
        mock_check_password.assert_called_once_with('wrong_password', 'hashed_password')
    
    @patch('app.models.user.get_db')
    def test_authenticate_user_not_found(self, mock_get_db):
        """Test authenticating with an email that doesn't exist."""
        # Setup mocks
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = None  # No user found with this email
        mock_get_db.return_value = mock_db
        
        # Try to authenticate with non-existent email
        user = User.authenticate('nonexistent@example.com', 'password123')
        
        # Assert authentication failed
        self.assertIsNone(user)
        
        # Verify the mock was called correctly
        mock_db.Users.find_one.assert_called_once_with({'email': 'nonexistent@example.com', 'deletedAt': None})
    
    @patch('app.models.user.get_db')
    def test_authenticate_deleted_user(self, mock_get_db):
        """Test authenticating a user that has been deleted."""
        # Setup mocks - create a deleted user
        deleted_user = self.mock_db_user.copy()
        deleted_user['deletedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = None  # No active user with this email
        mock_get_db.return_value = mock_db
        
        # Try to authenticate the deleted user
        user = User.authenticate('test@example.com', 'password123')
        
        # Assert authentication failed
        self.assertIsNone(user)
        
        # Verify the mock was called correctly
        mock_db.Users.find_one.assert_called_once_with({'email': 'test@example.com', 'deletedAt': None})


if __name__ == '__main__':
    unittest.main() 