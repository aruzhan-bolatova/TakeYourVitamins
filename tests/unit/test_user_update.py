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


class TestUserProfileUpdate(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        # Sample user data with ObjectId
        self.test_user_data = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),  # MongoDB ObjectId format
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
    
    @patch('app.models.user.get_db')
    @patch('app.models.user.User.validate_email')
    @patch('app.models.user.User.is_email_unique')
    def test_update_profile_success(self, mock_is_email_unique, mock_validate_email, mock_get_db):
        """Test successful profile update."""
        # Create mock DB and responses
        mock_db = MagicMock()
        # First find returns the user
        mock_db.Users.find_one.return_value = self.test_user_data
        
        # Setup the return after update
        updated_user_data = self.test_user_data.copy()
        updated_user_data['name'] = 'Updated Name'
        updated_user_data['email'] = 'updated@example.com'
        updated_user_data['age'] = 31
        updated_user_data['updatedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # After update, find_one should return the updated user
        mock_db.Users.find_one.side_effect = [self.test_user_data, updated_user_data]
        
        mock_get_db.return_value = mock_db
        mock_validate_email.return_value = True
        mock_is_email_unique.return_value = True
        
        # Perform the update
        update_data = {
            'name': 'Updated Name',
            'email': 'updated@example.com',
            'age': 31
        }
        updated_user = User.update(self.test_user_data['_id'], update_data)
        
        # Assert user was updated correctly
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.name, 'Updated Name')
        self.assertEqual(updated_user.email, 'updated@example.com')
        self.assertEqual(updated_user.age, 31)
        self.assertEqual(updated_user.user_id, self.test_user_data['userId'])
        
        # Verify the database calls were made
        mock_db.Users.find_one.assert_called()
        mock_db.Users.update_one.assert_called_once()
        mock_validate_email.assert_called_once_with('updated@example.com')
        mock_is_email_unique.assert_called_once_with('updated@example.com', self.test_user_data['_id'])
    
    @patch('app.models.user.get_db')
    @patch('app.models.user.User.validate_email')
    def test_update_profile_invalid_email(self, mock_validate_email, mock_get_db):
        """Test profile update with invalid email format."""
        # Setup mocks
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = self.test_user_data
        mock_get_db.return_value = mock_db
        
        # Mock email validation to fail
        mock_validate_email.return_value = False
        
        # Attempt to update with invalid email
        update_data = {
            'name': 'Updated Name',
            'email': 'invalid-email',  # Invalid email format
            'age': 31
        }
        
        # Should raise ValueError
        with self.assertRaises(ValueError) as context:
            User.update(self.test_user_data['_id'], update_data)
        
        # Check error message
        self.assertEqual(str(context.exception), 'Invalid email format')
        
        # Verify the validation was called
        mock_validate_email.assert_called_once_with('invalid-email')
    
    @patch('app.models.user.get_db')
    @patch('app.models.user.User.validate_email')
    @patch('app.models.user.User.is_email_unique')
    def test_update_profile_duplicate_email(self, mock_is_email_unique, mock_validate_email, mock_get_db):
        """Test profile update with email that already exists."""
        # Setup mocks
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = self.test_user_data
        mock_get_db.return_value = mock_db
        
        # Mock email validation to pass but uniqueness check to fail
        mock_validate_email.return_value = True
        mock_is_email_unique.return_value = False
        
        # Attempt to update with duplicate email
        update_data = {
            'name': 'Updated Name',
            'email': 'existing@example.com',  # Email that already exists
            'age': 31
        }
        
        # Should raise ValueError
        with self.assertRaises(ValueError) as context:
            User.update(self.test_user_data['_id'], update_data)
        
        # Check error message
        self.assertEqual(str(context.exception), 'Email already exists')
        
        # Verify the checks were called
        mock_validate_email.assert_called_once_with('existing@example.com')
        mock_is_email_unique.assert_called_once_with('existing@example.com', self.test_user_data['_id'])
    
    @patch('app.models.user.get_db')
    def test_update_profile_user_not_found(self, mock_get_db):
        """Test profile update for non-existent user."""
        # Setup mocks to return no user
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = None
        mock_get_db.return_value = mock_db
        
        # Attempt to update a non-existent user
        update_data = {
            'name': 'Updated Name',
            'age': 31
        }
        result = User.update(ObjectId('507f1f77bcf86cd799439099'), update_data)
        
        # Should return None for non-existent user
        self.assertIsNone(result)
        
        # Verify find_one was called with the correct ID
        mock_db.Users.find_one.assert_called_with({'_id': ObjectId('507f1f77bcf86cd799439099'), 'deletedAt': None})


if __name__ == '__main__':
    unittest.main() 