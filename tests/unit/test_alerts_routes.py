import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
import sys
import os
import json

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.routes.alerts import bp as alerts_bp

class TestAlertsRoutes(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Register blueprint
        self.app.register_blueprint(alerts_bp)

    def test_get_alerts(self):
        """Test the get_alerts endpoint."""
        # Make request
        response = self.client.get('/api/alerts/')
        
        # Assert response
        self.assertEqual(response.status_code, 501)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Alerts endpoint coming soon')


if __name__ == '__main__':
    unittest.main() 