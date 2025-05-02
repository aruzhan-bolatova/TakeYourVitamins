import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import datetime
from bson.objectid import ObjectId

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.models.user import User


class TestUserModel(unittest.TestCase):
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
            'password': 'hashed_password',
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
        
        # Verify the mocks were called correctly
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
        user = User.find_by_id(self.mock_object_id)
        
        # Assert the user was found and returned correctly
        self.assertIsNotNone(user)
        self.assertEqual(user.user_id, 'USER123456789')
        self.assertEqual(user.name, 'Test User')
        
        # Verify the mock was called correctly
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
        
        # Try to find a nonexistent user
        user = User.find_by_id(nonexistent_id)
        
        # Assert the user was not found
        self.assertIsNone(user)
        
        # Verify the mock was called correctly
        mock_db.Users.find_one.assert_called_once_with({'_id': nonexistent_id, 'deletedAt': None})
    
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
        updated_user = User.update(self.mock_object_id, update_data)
        
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
        mock_is_email_unique.assert_called_once_with('updated@example.com', self.mock_object_id)
    
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
            User.update(self.mock_object_id, update_data)
        
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
            User.update(self.mock_object_id, update_data)
        
        # Check error message
        self.assertEqual(str(context.exception), 'Email already exists')
        
        # Verify the checks were called
        mock_validate_email.assert_called_once_with('existing@example.com')
        mock_is_email_unique.assert_called_once_with('existing@example.com', self.mock_object_id)
    
    @patch('app.models.user.get_db')
    def test_update_profile_user_not_found(self, mock_get_db):
        """Test profile update for non-existent user."""
        # Setup mocks to return no user
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = None
        mock_get_db.return_value = mock_db
        
        # Create a mock ObjectId for a nonexistent user
        nonexistent_id = MagicMock()
        nonexistent_id.__str__.return_value = '507f1f77bcf86cd799439099'
        
        # Attempt to update a non-existent user
        update_data = {
            'name': 'Updated Name',
            'age': 31
        }
        result = User.update(nonexistent_id, update_data)
        
        # Should return None for non-existent user
        self.assertIsNone(result)
        
        # Verify find_one was called with the correct ID
        mock_db.Users.find_one.assert_called_with({'_id': nonexistent_id, 'deletedAt': None})
    
    @patch('app.models.user.get_db')
    def test_delete_user_success(self, mock_get_db):
        """Test successfully soft deleting a user."""
        # Setup mocks
        mock_db = MagicMock()
        # First find returns the user
        mock_db.Users.find_one.return_value = self.test_user_data
        
        # Setup a mock for the updated user with deletedAt set
        deleted_user_data = self.test_user_data.copy()
        deleted_user_data['deletedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # After delete, find_one should return the deleted user
        mock_db.Users.find_one.side_effect = [self.test_user_data, deleted_user_data]
        
        mock_get_db.return_value = mock_db
        
        # Perform the delete
        result = User.delete(self.mock_object_id)
        
        # Assert user was deleted correctly
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.deleted_at)
        self.assertEqual(result.user_id, self.test_user_data['userId'])
        
        # Verify the database calls were made
        mock_db.Users.update_one.assert_called_once()
    
    @patch('app.models.user.get_db')
    def test_delete_user_not_found(self, mock_get_db):
        """Test deleting a non-existent user."""
        # Setup mocks to return no user
        mock_db = MagicMock()
        mock_db.Users.find_one.return_value = None
        mock_get_db.return_value = mock_db
        
        # Create a mock ObjectId for a nonexistent user
        nonexistent_id = MagicMock()
        nonexistent_id.__str__.return_value = '507f1f77bcf86cd799439099'
        
        # Attempt to delete a non-existent user
        result = User.delete(nonexistent_id)
        
        # Should return None for non-existent user
        self.assertIsNone(result)
        
        # Verify find_one was called with the correct ID
        mock_db.Users.find_one.assert_called_with({'_id': nonexistent_id, 'deletedAt': None})


if __name__ == '__main__':
    unittest.main() 