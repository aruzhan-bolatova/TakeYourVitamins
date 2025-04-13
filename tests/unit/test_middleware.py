import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from functools import wraps

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.middleware.auth import admin_required, check_user_access
from flask import Flask, jsonify


class TestMiddleware(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        # Create a minimal Flask app for testing
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Mock user data
        self.regular_user = MagicMock()
        self.regular_user.user_id = 'USER123456789'
        self.regular_user.role = 'user'

        self.admin_user = MagicMock()
        self.admin_user.user_id = 'ADMIN123456789'
        self.admin_user.role = 'admin'

    def tearDown(self):
        """Tear down test fixtures after each test method is run."""
        self.app_context.pop()

    @patch('app.middleware.auth.verify_jwt_in_request')
    @patch('app.middleware.auth.get_jwt_identity')
    @patch('app.middleware.auth.User.find_by_id')
    def test_admin_required_with_admin_user(self, mock_find_by_id, mock_get_jwt_identity, mock_verify_jwt):
        """Test admin_required decorator with an admin user."""
        # Setup mocks
        mock_verify_jwt.return_value = None
        mock_get_jwt_identity.return_value = self.admin_user.user_id
        mock_find_by_id.return_value = self.admin_user

        # Create a test endpoint with the admin_required decorator
        @self.app.route('/test-admin')
        @admin_required
        def test_endpoint():
            return jsonify({'message': 'You have access'})

        # Create a test client
        client = self.app.test_client()

        # Make request
        response = client.get('/test-admin')

        # Assert response
        self.assertEqual(response.status_code, 200)
        mock_find_by_id.assert_called_once_with(self.admin_user.user_id)

    @patch('app.middleware.auth.verify_jwt_in_request')
    @patch('app.middleware.auth.get_jwt_identity')
    @patch('app.middleware.auth.User.find_by_id')
    def test_admin_required_with_regular_user(self, mock_find_by_id, mock_get_jwt_identity, mock_verify_jwt):
        """Test admin_required decorator with a regular user."""
        # Setup mocks
        mock_verify_jwt.return_value = None
        mock_get_jwt_identity.return_value = self.regular_user.user_id
        mock_find_by_id.return_value = self.regular_user

        # Create a test endpoint with the admin_required decorator
        @self.app.route('/test-admin-only')
        @admin_required
        def test_endpoint():
            return jsonify({'message': 'You have access'})

        # Create a test client
        client = self.app.test_client()

        # Make request
        response = client.get('/test-admin-only')

        # Assert response - should be forbidden
        self.assertEqual(response.status_code, 403)
        mock_find_by_id.assert_called_once_with(self.regular_user.user_id)

    @patch('app.middleware.auth.verify_jwt_in_request')
    @patch('app.middleware.auth.get_jwt_identity')
    @patch('app.middleware.auth.User.find_by_id')
    def test_check_user_access_same_user(self, mock_find_by_id, mock_get_jwt_identity, mock_verify_jwt):
        """Test check_user_access decorator when accessing own resources."""
        # Setup mocks
        mock_verify_jwt.return_value = None
        mock_get_jwt_identity.return_value = self.regular_user.user_id
        mock_find_by_id.return_value = self.regular_user

        # Create a test endpoint with the check_user_access decorator
        @self.app.route('/test-user/<user_id>')
        @check_user_access
        def test_endpoint(user_id):
            return jsonify({'message': 'You have access'})

        # Create a test client
        client = self.app.test_client()

        # Make request to own resource
        response = client.get(f'/test-user/{self.regular_user.user_id}')

        # Assert response
        self.assertEqual(response.status_code, 200)

    @patch('app.middleware.auth.verify_jwt_in_request')
    @patch('app.middleware.auth.get_jwt_identity')
    @patch('app.middleware.auth.User.find_by_id')
    def test_check_user_access_different_user(self, mock_find_by_id, mock_get_jwt_identity, mock_verify_jwt):
        """Test check_user_access decorator when accessing another user's resources."""
        # Setup mocks
        mock_verify_jwt.return_value = None
        mock_get_jwt_identity.return_value = self.regular_user.user_id
        mock_find_by_id.return_value = self.regular_user

        # Create a test endpoint with the check_user_access decorator
        @self.app.route('/test-user/<user_id>')
        @check_user_access
        def test_endpoint(user_id):
            return jsonify({'message': 'You have access'})

        # Create a test client
        client = self.app.test_client()

        # Make request to another user's resource
        other_user_id = 'OTHER123456789'
        response = client.get(f'/test-user/{other_user_id}')

        # Assert response - should be forbidden
        self.assertEqual(response.status_code, 403)

    @patch('app.middleware.auth.verify_jwt_in_request')
    @patch('app.middleware.auth.get_jwt_identity')
    @patch('app.middleware.auth.User.find_by_id')
    def test_check_user_access_admin_accessing_other_user(self, mock_find_by_id, mock_get_jwt_identity, mock_verify_jwt):
        """Test check_user_access decorator when an admin accesses another user's resources."""
        # Setup mocks
        mock_verify_jwt.return_value = None
        mock_get_jwt_identity.return_value = self.admin_user.user_id
        mock_find_by_id.return_value = self.admin_user

        # Create a test endpoint with the check_user_access decorator
        @self.app.route('/test-user/<user_id>')
        @check_user_access
        def test_endpoint(user_id):
            return jsonify({'message': 'You have access'})

        # Create a test client
        client = self.app.test_client()

        # Make request to another user's resource as admin
        other_user_id = 'OTHER123456789'
        response = client.get(f'/test-user/{other_user_id}')

        # Assert response - admin should be allowed
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main() 