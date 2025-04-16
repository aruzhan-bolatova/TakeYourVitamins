import unittest
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId
from app.models.supplement import Supplement


class TestSupplement(unittest.TestCase):

    def setUp(self):
        """Set up common test data."""
        self.valid_data = {
            "supplementId": "SUPP101",
            "name": "Vitamin C",
            "aliases": ["Ascorbic Acid"],
            "description": "Boosts immunity and acts as an antioxidant.",
            "intakePractices": {
                "dosage": "500mg daily",
                "timing": "Morning",
                "specialInstructions": "Take with food."
            },
            "scientificDetails": {
                "benefits": ["Boosts immunity", "Antioxidant"],
                "sideEffects": ["Rare at recommended doses"]
            },
            "category": "Vitamins",
            "updatedAt": "2023-01-01T00:00:00Z"
        }

    def test_validate_data_valid(self):
        """Test validate_data with valid data."""
        supplement = Supplement(self.valid_data)
        try:
            supplement.validate_data(self.valid_data)
        except ValueError:
            self.fail("validate_data raised ValueError unexpectedly!")

    def test_validate_data_missing_required_fields(self):
        """Test validate_data with missing required fields."""
        invalid_data = {
            "name": "Vitamin C"
        }
        supplement = Supplement(invalid_data)
        with self.assertRaises(ValueError) as context:
            supplement.validate_data(invalid_data)
        self.assertEqual(str(context.exception), "Missing required field: supplementId")

    def test_to_dict_all_fields(self):
        """Test to_dict with all fields populated."""
        supplement = Supplement(self.valid_data)
        result = supplement.to_dict()
        self.assertEqual(result["supplementId"], "SUPP101")
        self.assertEqual(result["name"], "Vitamin C")
        self.assertEqual(result["aliases"], ["Ascorbic Acid"])
        self.assertEqual(result["description"], "Boosts immunity and acts as an antioxidant.")
        self.assertEqual(result["category"], "Vitamins")
        self.assertEqual(result["updatedAt"], "2023-01-01T00:00:00Z")

    def test_to_dict_missing_optional_fields(self):
        """Test to_dict with some optional fields missing."""
        partial_data = {
            "supplementId": "SUPP102",
            "name": "Magnesium",
            "description": "Essential mineral for muscle and nerve function."
        }
        supplement = Supplement(partial_data)
        result = supplement.to_dict()
        self.assertEqual(result["supplementId"], "SUPP102")
        self.assertEqual(result["name"], "Magnesium")
        self.assertEqual(result["description"], "Essential mineral for muscle and nerve function.")
        self.assertEqual(result["aliases"], [])
        self.assertIsNone(result["updatedAt"])

    @patch("app.models.supplement.get_db")
    def test_find_by_id_valid(self, mock_get_db):
        """Test find_by_id with a valid _id."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.Supplements.find_one.return_value = self.valid_data

        supplement = Supplement.find_by_id(ObjectId("507f1f77bcf86cd799439011"))
        self.assertIsNotNone(supplement)
        self.assertEqual(supplement.name, "Vitamin C")

    @patch("app.models.supplement.get_db")
    def test_find_by_id_not_found(self, mock_get_db):
        """Test find_by_id with a non-existent _id."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.Supplements.find_one.return_value = None

        supplement = Supplement.find_by_id(ObjectId("507f1f77bcf86cd799439011"))
        self.assertIsNone(supplement)

    @patch("app.models.supplement.get_db")
    def test_update_valid(self, mock_get_db):
        """Test update with valid data."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.Supplements.find_one.return_value = self.valid_data

        Supplement.update(ObjectId("507f1f77bcf86cd799439011"), {"description": "Updated description"})
        mock_db.Supplements.update_one.assert_called_once_with(
            {"_id": ObjectId("507f1f77bcf86cd799439011")},
            {"$set": {"description": "Updated description"}}
        )

    @patch("app.models.supplement.get_db")
    def test_update_not_found(self, mock_get_db):
        """Test update with a non-existent _id."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.Supplements.find_one.return_value = None

        with self.assertRaises(ValueError) as context:
            Supplement.update(ObjectId("507f1f77bcf86cd799439011"), {"description": "Updated description"})
        self.assertEqual(str(context.exception), "Error updating supplement: Supplement with ID 507f1f77bcf86cd799439011 not found.")

    @patch("app.models.supplement.get_db")
    def test_update_invalid_data(self, mock_get_db):
        """Test update with invalid data (missing required fields)."""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.Supplements.find_one.return_value = self.valid_data

        with self.assertRaises(ValueError) as context:
            Supplement.update(ObjectId("507f1f77bcf86cd799439011"), {"name": ""})
        self.assertIn("Missing required field", str(context.exception))


if __name__ == "__main__":
    unittest.main()