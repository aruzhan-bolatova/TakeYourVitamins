import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from bson.objectid import ObjectId
from datetime import datetime
import uuid



# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.supplement import Supplement
from app.models.user import User
from app.models.intake_log import IntakeLog


class TestSupplements(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method is run."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['JWT_ENABLED'] = False  # Disable JWT for testing
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Generate test user IDs
        self.test_user_id = f"TEST_USER_{uuid.uuid4().hex[:8]}"
        self.test_admin_id = f"ADMIN_USER_{uuid.uuid4().hex[:8]}"
        
        # Mock users for permission tests
        self.mock_user = MagicMock()
        self.mock_user.user_id = self.test_user_id
        self.mock_user.role = "user"
        
        self.mock_admin = MagicMock()
        self.mock_admin.user_id = self.test_admin_id
        self.mock_admin.role = "admin"
        
        # Set up JWT mocking
        self.jwt_patcher = patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
        self.get_jwt_identity_patcher = patch('app.routes.supplements.get_jwt_identity')
        self.admin_required_patcher = patch('app.routes.supplements.admin_required')
        
        # Start the patchers
        self.mock_verify_jwt = self.jwt_patcher.start()
        self.mock_jwt_identity = self.get_jwt_identity_patcher.start()
        self.mock_admin_required = self.admin_required_patcher.start()
        
        # Configure mocks - default to regular user with admin permissions (for legacy tests)
        self.mock_verify_jwt.return_value = None  # Skip JWT verification
        self.mock_jwt_identity.return_value = self.test_user_id
        self.mock_admin_required.return_value = True  # Default to admin access for legacy tests
        
        # Mock ObjectId
        self.test_id = "507f1f77bcf86cd799439011"
        self.test_object_id = ObjectId(self.test_id)
        
        # Sample supplement data
        self.test_supplement_data = {
            "_id": self.test_id,
            "supplementId": "SUPP001",
            "name": "Vitamin D",
            "aliases": ["Cholecalciferol", "Vitamin D3"],
            "description": "Vitamin D is essential for bone health.",
            "intakePractices": {
                "dosage": "1000-2000 IU daily",
                "timing": "Morning with food",
                "specialInstructions": "Fat-soluble, best absorbed with meals containing fat."
            },
            "scientificDetails": {
                "benefits": ["Bone health", "Immune support"],
                "sideEffects": ["Rare at recommended doses"]
            },
            "category": "Vitamins",
            "updatedAt": None
        }
        
        # Mock supplement object
        self.mock_supplement = MagicMock()
        self.mock_supplement._id = self.test_id
        self.mock_supplement.supplement_id = self.test_supplement_data["supplementId"]
        self.mock_supplement.name = self.test_supplement_data["name"]
        self.mock_supplement.aliases = self.test_supplement_data["aliases"]
        self.mock_supplement.description = self.test_supplement_data["description"]
        self.mock_supplement.intake_practices = self.test_supplement_data["intakePractices"]
        self.mock_supplement.scientific_details = self.test_supplement_data["scientificDetails"]
        self.mock_supplement.category = self.test_supplement_data["category"]
        self.mock_supplement.updated_at = self.test_supplement_data["updatedAt"]
        self.mock_supplement.to_dict.return_value = self.test_supplement_data
        
        # Sample intake log data
        timestamp = datetime.now().isoformat()
        self.test_intake_log_data = {
            "_id": str(ObjectId()),
            "intakeLogId": f"INTAKE_{uuid.uuid4().hex[:8]}",
            "userId": self.test_user_id,
            "supplementId": self.test_id,
            "timestamp": timestamp,
            "dosage": "1000 IU",
            "notes": "Taken with breakfast",
            "createdAt": timestamp,
            "updatedAt": None,
            "isDeleted": False
        }
        
        # Mock intake log
        self.mock_intake_log = MagicMock()
        self.mock_intake_log._id = self.test_intake_log_data["_id"]
        self.mock_intake_log.intake_log_id = self.test_intake_log_data["intakeLogId"]
        self.mock_intake_log.user_id = self.test_intake_log_data["userId"]
        self.mock_intake_log.supplement_id = self.test_intake_log_data["supplementId"]
        self.mock_intake_log.timestamp = self.test_intake_log_data["timestamp"]
        self.mock_intake_log.dosage = self.test_intake_log_data["dosage"]
        self.mock_intake_log.notes = self.test_intake_log_data["notes"]
        self.mock_intake_log.created_at = self.test_intake_log_data["createdAt"]
        self.mock_intake_log.updated_at = self.test_intake_log_data["updatedAt"]
        self.mock_intake_log.is_deleted = self.test_intake_log_data["isDeleted"]
        self.mock_intake_log.to_dict.return_value = self.test_intake_log_data
    
    def tearDown(self):
        """Tear down test fixtures after each test method is run."""
        # Stop the patchers
        self.jwt_patcher.stop()
        self.get_jwt_identity_patcher.stop()
        self.admin_required_patcher.stop()
        self.app_context.pop()
    
    # GET /api/supplements/ - Get supplements with pagination
    @patch('app.routes.supplements.get_db')
    def test_get_supplements_with_pagination(self, mock_get_db):
        """Test getting supplements with pagination."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.Supplements = mock_collection
        mock_get_db.return_value = mock_db
        
        # Setup mock query results
        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = [self.test_supplement_data]
        mock_collection.find.return_value = mock_cursor
        mock_collection.count_documents.return_value = 15  # Total of 15 supplements
        
        # Make request with pagination
        response = self.client.get('/api/supplements/?page=2&limit=5')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["supplements"]), 1)
        self.assertEqual(data["supplements"][0]["name"], "Vitamin D")
        
        # Verify pagination info is correct
        pagination = data["pagination"]
        self.assertEqual(pagination["page"], 2)
        self.assertEqual(pagination["limit"], 5)
        self.assertEqual(pagination["totalItems"], 15)
        self.assertEqual(pagination["totalPages"], 3)
        self.assertTrue(pagination["hasPrev"])
        self.assertTrue(pagination["hasNext"])
        
        # Verify correct skip and limit were used
        mock_cursor.skip.assert_called_once_with(5)  # Skip first 5 items (page 1)
        mock_cursor.limit.assert_called_once_with(5)  # Limit to 5 items per page
    
    @patch('app.routes.supplements.get_db')
    def test_get_supplements_with_category_filter(self, mock_get_db):
        """Test getting supplements with category filter."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.Supplements = mock_collection
        mock_get_db.return_value = mock_db
        
        # Setup mock query results
        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = [self.test_supplement_data]
        mock_collection.find.return_value = mock_cursor
        mock_collection.count_documents.return_value = 3  # 3 vitamins
        
        # Make request with category filter
        response = self.client.get('/api/supplements/?category=Vitamins')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["supplements"]), 1)
        
        # Verify correct query was used
        expected_query = {
            'category': {'$regex': 'Vitamins', '$options': 'i'},
            'deletedAt': {'$exists': False}
        }
        mock_collection.find.assert_called_once()
        call_args = mock_collection.find.call_args[0][0]
        self.assertIn('category', call_args)
        self.assertIn('deletedAt', call_args)
    
    # Test autocomplete endpoint
    @patch('app.routes.supplements.get_db')
    def test_autocomplete_supplements(self, mock_get_db):
        """Test autocomplete for supplement names."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.Supplements = mock_collection
        mock_get_db.return_value = mock_db
        
        # Setup mock document data
        mock_supplement = {
            "_id": self.test_object_id,
            "supplementId": "SUPP001",
            "name": "Vitamin D",
            "aliases": ["Cholecalciferol", "Vitamin D3"],
            "category": "Vitamins"
        }
        
        # Create a proper mock cursor that can be chained and iterated
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = [mock_supplement]  # Return list for iteration
        mock_collection.find.return_value = mock_cursor
        
        # Make request to autocomplete endpoint
        response = self.client.get('/api/supplements/autocomplete?q=vita')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1, f"Expected 1 result, got: {data}")
        
        # Verify find was called with correct parameters
        mock_collection.find.assert_called_once()
        # First argument is the query
        find_args = mock_collection.find.call_args[0][0]
        self.assertIn('$or', find_args)
        self.assertIn('deletedAt', find_args)
        # Second argument should be the projection
        self.assertEqual(len(mock_collection.find.call_args[0]), 2, "find() should be called with a projection")
    
    # Test search endpoint
    @patch('app.routes.supplements.get_db')
    def test_search_supplements(self, mock_get_db):
        """Test searching supplements by keyword."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.Supplements = mock_collection
        mock_get_db.return_value = mock_db
        
        # Create a proper mock cursor that can be chained and iterated
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = [self.test_supplement_data]  # Return list for iteration
        mock_collection.find.return_value = mock_cursor
        
        # Make request to search endpoint
        response = self.client.get('/api/supplements/search?q=bone')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1, f"Expected 1 result, got: {data}")
        self.assertEqual(data["results"][0]["name"], "Vitamin D")
        
        # Verify correct query was used
        mock_collection.find.assert_called_once()
        find_args = mock_collection.find.call_args[0][0]
        self.assertIn('$or', find_args)
        self.assertIn('deletedAt', find_args)
    
    # GET /api/supplements/ - Get all supplements with optional search
    @patch('app.routes.supplements.get_db')
    def test_get_supplements_no_search(self, mock_get_db):
        """Test getting all supplements with no search query."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.Supplements = mock_collection
        mock_get_db.return_value = mock_db
        
        # Setup mock query results
        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = [self.test_supplement_data]
        mock_collection.find.return_value = mock_cursor
        mock_collection.count_documents.return_value = 1
        
        # Make request
        response = self.client.get('/api/supplements/')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("supplements", data)
        self.assertEqual(len(data["supplements"]), 1)
        self.assertEqual(data["supplements"][0]["supplementId"], "SUPP001")
        self.assertEqual(data["supplements"][0]["name"], "Vitamin D")
        
        # Verify pagination info is present
        self.assertIn("pagination", data)
        self.assertEqual(data["pagination"]["totalItems"], 1)
    
    @patch('app.routes.supplements.get_db')
    def test_get_supplements_with_search(self, mock_get_db):
        """Test getting supplements with a search query."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.Supplements = mock_collection
        mock_get_db.return_value = mock_db
        
        # Setup mock query results
        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = [self.test_supplement_data]
        mock_collection.find.return_value = mock_cursor
        mock_collection.count_documents.return_value = 1
        
        # Make request with search query
        response = self.client.get('/api/supplements/?search=vitamin')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("supplements", data)
        self.assertEqual(len(data["supplements"]), 1)
        self.assertEqual(data["supplements"][0]["name"], "Vitamin D")
    
    @patch('app.routes.supplements.get_db')
    def test_get_supplements_empty_results(self, mock_get_db):
        """Test getting supplements with no results."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.Supplements = mock_collection
        mock_get_db.return_value = mock_db
        
        # Setup mock query results
        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        mock_collection.find.return_value = mock_cursor
        mock_collection.count_documents.return_value = 0
        
        # Make request
        response = self.client.get('/api/supplements/?search=nonexistent')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("supplements", data)
        self.assertEqual(len(data["supplements"]), 0)
    
    # GET /api/supplements/<supplement_id> - Get a specific supplement
    @patch('app.models.supplement.Supplement.find_by_id')
    def test_get_supplement_by_id_success(self, mock_find_by_id):
        """Test getting a specific supplement by ID successfully."""
        # Setup mock
        mock_find_by_id.return_value = self.mock_supplement
        
        # Make request
        response = self.client.get(f'/api/supplements/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["supplementId"], "SUPP001")
        self.assertEqual(data["name"], "Vitamin D")
        
        # Verify mock was called with correct ID
        mock_find_by_id.assert_called_once_with(self.test_object_id)
    
    @patch('app.models.supplement.Supplement.find_by_id')
    def test_get_supplement_by_id_not_found(self, mock_find_by_id):
        """Test getting a non-existent supplement by ID."""
        # Setup mock to return None
        mock_find_by_id.return_value = None
        
        # Make request
        response = self.client.get(f'/api/supplements/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Supplement not found")
        
        # Verify mock was called
        mock_find_by_id.assert_called_once()
    
    def test_get_supplement_by_id_invalid_id(self):
        """Test getting a supplement with an invalid ID format."""
        # Make request with invalid ID
        response = self.client.get('/api/supplements/invalid_id')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Invalid ID format")
    
    # POST /api/supplements/ - Create a new supplement
    @patch('app.routes.supplements.get_db')
    def test_create_supplement_success(self, mock_get_db):
        """Test creating a new supplement successfully with correct path patching."""
        import uuid
        import time
        
        # Generate a unique ID and name for this test
        unique_id = f"TEST_SUPP_{uuid.uuid4().hex[:8]}_{int(time.time())}"
        unique_name = f"Zinc Test {uuid.uuid4().hex[:8]} {int(time.time())}"
        
        # Setup mock DB
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.Supplements = mock_collection
        mock_get_db.return_value = mock_db
        
        # Setup insert_one mock
        mock_result = MagicMock()
        mock_result.inserted_id = self.test_object_id
        mock_collection.insert_one.return_value = mock_result

        # Make request with unique data
        new_supplement = {
            "supplementId": unique_id,
            "name": unique_name,
            "description": "Essential mineral for immune function.",
            "aliases": ["Zinc Gluconate", "Zinc Picolinate"],
            "category": "Minerals"
        }
        
        response = self.client.post(
            '/api/supplements/',
            data=json.dumps(new_supplement),
            content_type='application/json'
        )
        
        # Assert response status and data
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["message"], "Supplement created successfully")
        self.assertIn("_id", data)
        
        # Verify the mock DB was used - we just need to confirm insert_one was called
        # rather than checking exact arguments since the Supplement object modifies the data
        mock_collection.insert_one.assert_called_once()
    
    def test_create_supplement_missing_fields(self):
        """Test creating a supplement with missing required fields."""
        # Make request with missing description
        incomplete_data = {
            "supplementId": "SUPP099",
            "name": "Zinc"
            # Missing description
        }
        
        response = self.client.post(
            '/api/supplements/',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required field", data["error"])
    
    def test_create_supplement_not_json(self):
        """Test creating a supplement with non-JSON content."""
        # Make request with non-JSON content
        response = self.client.post(
            '/api/supplements/',
            data="This is not JSON",
            content_type='text/plain'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Missing JSON in request")
    
    def test_create_supplement_empty_data(self):
        """Test creating a supplement with empty data."""
        # Make request with empty JSON
        response = self.client.post(
            '/api/supplements/',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Empty supplement data")
    
    @patch('app.routes.supplements.get_db')
    def test_create_supplement_database_error(self, mock_get_db):
        """Test error handling when database operation fails."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.Supplements = mock_collection
        mock_get_db.return_value = mock_db
        
        # Setup insert_one mock to return a failed result
        mock_result = MagicMock()
        mock_result.inserted_id = None  # This indicates insertion failed
        mock_collection.insert_one.return_value = mock_result
        
        # Make request with valid data
        new_supplement = {
            "supplementId": "SUPP100",
            "name": "Magnesium",
            "description": "Essential mineral for muscle and nerve function.",
            "category": "Minerals"
        }
        
        response = self.client.post(
            '/api/supplements/',
            data=json.dumps(new_supplement),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data["error"], "Failed to insert supplement")
    
    @patch('app.routes.supplements.get_db')
    def test_create_supplement_general_exception(self, mock_get_db):
        """Test general exception handling during supplement creation."""
        # Setup mock DB to raise an exception
        mock_get_db.side_effect = Exception("Database connection error")
        
        # Make request with valid data
        new_supplement = {
            "supplementId": "SUPP101",
            "name": "Iron",
            "description": "Essential mineral for blood production.",
            "category": "Minerals"
        }
        
        response = self.client.post(
            '/api/supplements/',
            data=json.dumps(new_supplement),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data["error"], "An error occurred")
        self.assertIn("Database connection error", data["details"])
    
    # PUT /api/supplements/<supplement_id> - Update a supplement
    @patch('app.models.supplement.Supplement.update')
    def test_update_supplement_success(self, mock_update):
        """Test updating a supplement successfully."""
        # Make request
        update_data = {
            "description": "Updated description for Vitamin D."
        }
        
        response = self.client.put(
            f'/api/supplements/{self.test_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Supplement updated successfully")
        
        # Verify mock was called
        mock_update.assert_called_once_with(self.test_object_id, update_data)
    
    @patch('app.models.supplement.Supplement.update')
    def test_update_supplement_not_found(self, mock_update):
        """Test updating a non-existent supplement."""
        # Setup mock to raise ValueError
        mock_update.side_effect = ValueError("Supplement not found")
        
        # Make request
        update_data = {
            "description": "Updated description for nonexistent supplement."
        }
        
        response = self.client.put(
            f'/api/supplements/{self.test_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Supplement not found")
    
    @patch('app.models.supplement.Supplement.update')
    def test_update_supplement_general_exception(self, mock_update):
        """Test handling general exceptions during supplement update."""
        # Setup mock to raise a general exception
        mock_update.side_effect = Exception("Database error")
        
        # Make request
        update_data = {
            "description": "Updated description for Vitamin D."
        }
        
        response = self.client.put(
            f'/api/supplements/{self.test_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data["error"], "An error occurred")
        self.assertEqual(data["details"], "Database error")
    
    # DELETE /api/supplements/<supplement_id> - Delete a supplement
    @patch('app.models.supplement.Supplement.delete')
    def test_delete_supplement_success_soft(self, mock_delete):
        """Test soft deleting a supplement successfully."""
        # Setup mock
        mock_delete.return_value = True
        
        # Make request for soft delete (default)
        response = self.client.delete(f'/api/supplements/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Supplement deleted successfully")
        
        # Verify mock was called with soft_delete=True
        mock_delete.assert_called_with(self.test_object_id, soft_delete=True)
    
    @patch('app.models.supplement.Supplement.delete')
    def test_delete_supplement_success_hard(self, mock_delete):
        """Test hard deleting a supplement successfully."""
        # Setup mock
        mock_delete.return_value = True
        
        # Make request for hard delete
        response = self.client.delete(f'/api/supplements/{self.test_id}?soft=false')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Supplement deleted successfully")
        
        # Verify mock was called with soft_delete=False
        mock_delete.assert_called_with(self.test_object_id, soft_delete=False)
    
    @patch('app.models.supplement.Supplement.delete')
    def test_delete_supplement_not_found(self, mock_delete):
        """Test deleting a non-existent supplement."""
        # Setup mock to return False (not found)
        mock_delete.return_value = False
        
        # Make request
        response = self.client.delete(f'/api/supplements/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Supplement not found")
    
    @patch('app.models.supplement.Supplement.delete')
    def test_delete_supplement_general_exception(self, mock_delete):
        """Test handling general exceptions during supplement deletion."""
        # Setup mock to raise a general exception
        mock_delete.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.delete(f'/api/supplements/{self.test_id}')
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data["error"], "An error occurred")
        self.assertEqual(data["details"], "Database error")


if __name__ == '__main__':
    unittest.main()
