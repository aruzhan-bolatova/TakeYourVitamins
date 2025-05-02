import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.models.user import User

class TestEmailValidation(unittest.TestCase):
    def test_validate_email_valid(self):
        """Test valid email formats"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.com',
            'user-name@domain.co.uk',
            'user123@sub.domain.org'
        ]
        
        for email in valid_emails:
            self.assertTrue(User.validate_email(email))
    
    def test_validate_email_invalid(self):
        """Test invalid email formats"""
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

if __name__ == '__main__':
    unittest.main() 