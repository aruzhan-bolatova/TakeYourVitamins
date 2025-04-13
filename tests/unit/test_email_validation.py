import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.models.user import User


class TestEmailValidation(unittest.TestCase):
    def test_valid_email_formats(self):
        """Test validation of valid email formats."""
        valid_emails = [
            'test@example.com',
            'user.name@example.com',
            'user+tag@example.com',
            'user_name@example.co.uk',
            'user123@subdomain.example.com'
        ]
        
        for email in valid_emails:
            self.assertTrue(
                User.validate_email(email), 
                f"Email {email} should be valid but was rejected"
            )
    
    def test_invalid_email_formats(self):
        """Test validation of invalid email formats."""
        invalid_emails = [
            '',                      # Empty
            'plaintext',             # No domain part
            '@example.com',          # No username part
            'user@',                 # No domain
            'user@example',          # No TLD
            'user@.com',             # No domain name
            'user name@example.com', # Space in username
            'user@exam ple.com',     # Space in domain
            'user@example..com'      # Double period
        ]
        
        for email in invalid_emails:
            self.assertFalse(
                User.validate_email(email), 
                f"Email {email} should be invalid but was accepted"
            )
    
    @patch('app.models.user.get_db')
    def test_email_uniqueness_check(self, mock_get_db):
        """Test the email uniqueness check."""
        # Mock database with existing user
        existing_email = 'existing@example.com'
        
        mock_db = MagicMock()
        # Email exists case
        mock_db.Users.find_one.return_value = {'email': existing_email}
        mock_get_db.return_value = mock_db
        
        # Test email that already exists
        self.assertFalse(
            User.is_email_unique(existing_email),
            "Email should not be unique but was reported as unique"
        )
        
        # Test email uniqueness with exclusion
        user_id = 'USER123'
        # Configure mock to return None when checking for duplicate with exclusion
        mock_db.Users.find_one.return_value = None
        
        self.assertTrue(
            User.is_email_unique(existing_email, user_id),
            "Email should be unique when excluding the current user but was reported as not unique"
        )
        
        # Verify correct query was used with exclusion
        mock_db.Users.find_one.assert_called_with({
            'email': existing_email, 
            'deletedAt': None,
            'userId': {'$ne': user_id}
        })


if __name__ == '__main__':
    unittest.main() 