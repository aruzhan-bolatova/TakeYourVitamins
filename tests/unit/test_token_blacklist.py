import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import datetime

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.models.token_blacklist import TokenBlacklist


class TestTokenBlacklist(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        # Sample token data
        now = datetime.datetime.now(datetime.timezone.utc)
        self.test_token_data = {
            'jti': 'test_jti_123456',
            'type': 'access',
            'userId': 'USER123456789',
            'revokedAt': now.isoformat(),
            'expiresAt': (now + datetime.timedelta(days=1)).isoformat()
        }
    
    @patch('app.models.token_blacklist.get_db')
    def test_add_to_blacklist(self, mock_get_db):
        """Test adding a token to the blacklist."""
        # Setup mock
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Prepare data
        jti = self.test_token_data['jti']
        token_type = self.test_token_data['type']
        user_id = self.test_token_data['userId']
        expires_at = datetime.datetime.fromisoformat(self.test_token_data['expiresAt'])
        
        # Call the method
        result = TokenBlacklist.add_to_blacklist(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            expires_at=expires_at
        )
        
        # Assert result
        self.assertIsInstance(result, TokenBlacklist)
        self.assertEqual(result.jti, jti)
        self.assertEqual(result.token_type, token_type)
        self.assertEqual(result.user_id, user_id)
        
        # Verify mock calls
        mock_db.TokenBlacklist.insert_one.assert_called_once()
    
    @patch('app.models.token_blacklist.get_db')
    def test_is_blacklisted_true(self, mock_get_db):
        """Test checking if a token is blacklisted when it is."""
        # Setup mock
        mock_db = MagicMock()
        mock_db.TokenBlacklist.find_one.return_value = self.test_token_data
        mock_get_db.return_value = mock_db
        
        # Call the method
        result = TokenBlacklist.is_blacklisted(self.test_token_data['jti'])
        
        # Assert result
        self.assertTrue(result)
        
        # Verify mock calls
        mock_db.TokenBlacklist.find_one.assert_called_once_with({'jti': self.test_token_data['jti']})
    
    @patch('app.models.token_blacklist.get_db')
    def test_is_blacklisted_false(self, mock_get_db):
        """Test checking if a token is blacklisted when it is not."""
        # Setup mock
        mock_db = MagicMock()
        mock_db.TokenBlacklist.find_one.return_value = None
        mock_get_db.return_value = mock_db
        
        # Call the method
        result = TokenBlacklist.is_blacklisted('non_existent_jti')
        
        # Assert result
        self.assertFalse(result)
        
        # Verify mock calls
        mock_db.TokenBlacklist.find_one.assert_called_once_with({'jti': 'non_existent_jti'})


if __name__ == '__main__':
    unittest.main() 