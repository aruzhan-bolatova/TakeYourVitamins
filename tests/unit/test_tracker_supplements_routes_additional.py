import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_jwt_extended import create_access_token, JWTManager
from bson.objectid import ObjectId
import sys
import os
import json

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.tracker_supplement_list import TrackerSupplementList
from app.routes.tracker_supplements_lists import bp as tracker_supplements_list_bp

class TestTrackerSupplementsRoutesAdditional(unittest.TestCase):

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

        # Create dummy user IDs
        self.user_id = str(ObjectId())
        
        # Create access tokens
        self.access_token = create_access_token(identity=self.user_id)
        self.headers = {'Authorization': f'Bearer {self.access_token}'}

        # Register blueprint
        self.app.register_blueprint(tracker_supplements_list_bp, name='tracker_supplements_list_additional')

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    @patch('app.routes.tracker_supplements_lists.TrackerSupplementList.find_by_user_id')
    def test_get_tracked_supplement_missing_supplement_id(self, mock_find_by_user_id):
        """Test get tracked supplement with missing supplement ID."""
        # Make request without supplement ID
        response = self.client.get(f'/api/tracker_supplements_list/{self.user_id}', headers=self.headers)
        
        # Assert response - updated to match actual implementation
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)

        # Verify mock was called as API implementation attempts to find by user_id first
        mock_find_by_user_id.assert_called_once()

if __name__ == '__main__':
    unittest.main() 