import unittest
from unittest.mock import patch, MagicMock
import json
import datetime
from bson.objectid import ObjectId

# Mock the interactions module which is imported in tracker_supplements_list.py
import sys
import os

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

sys.modules['interactions'] = MagicMock()

from app import create_app
from app.models.tracker_supplement_list import TrackerSupplementList, TrackedSupplement
from flask_jwt_extended import create_access_token
from flask import Blueprint, jsonify


class TestTrackedSupplement(unittest.TestCase):
    """Test case for the TrackedSupplement model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.supplement_data = {
            'supplementId': str(ObjectId()),
            'supplementName': 'Vitamin D',
            'dosage': 1000,
            'unit': 'mg',
            'frequency': 'daily',
            'duration': '30 days',
            'startDate': '2023-04-01T00:00:00',
            'endDate': '2023-05-01T00:00:00',
            'notes': 'Take with food',
            'createdAt': '2023-04-01T00:00:00',
            'updatedAt': '2023-04-01T00:00:00'
        }
        
    def test_init(self):
        """Test initialization of TrackedSupplement."""
        supplement = TrackedSupplement(self.supplement_data)
        
        self.assertEqual(supplement.supplement_id, self.supplement_data['supplementId'])
        self.assertEqual(supplement.supplement_name, 'Vitamin D')
        self.assertEqual(supplement.dosage, 1000)
        self.assertEqual(supplement.unit, 'mg')
        self.assertEqual(supplement.frequency, 'daily')
        self.assertEqual(supplement.duration, '30 days')
        self.assertEqual(supplement.start_date, '2023-04-01T00:00:00')
        self.assertEqual(supplement.end_date, '2023-05-01T00:00:00')
        self.assertEqual(supplement.notes, 'Take with food')
        self.assertEqual(supplement.created_at, '2023-04-01T00:00:00')
        self.assertEqual(supplement.updated_at, '2023-04-01T00:00:00')
    
    def test_to_dict(self):
        """Test converting TrackedSupplement to dictionary."""
        supplement = TrackedSupplement(self.supplement_data)
        result = supplement.to_dict()
        
        self.assertEqual(result['supplementId'], self.supplement_data['supplementId'])
        self.assertEqual(result['supplementName'], 'Vitamin D')
        self.assertEqual(result['dosage'], 1000)
        self.assertEqual(result['unit'], 'mg')
        self.assertEqual(result['frequency'], 'daily')
        self.assertEqual(result['duration'], '30 days')
        self.assertEqual(result['startDate'], '2023-04-01T00:00:00')
        self.assertEqual(result['endDate'], '2023-05-01T00:00:00')
        self.assertEqual(result['notes'], 'Take with food')
        self.assertEqual(result['createdAt'], '2023-04-01T00:00:00')
        self.assertEqual(result['updatedAt'], '2023-04-01T00:00:00')
    
    def test_validate_data_valid(self):
        """Test validation with valid data."""
        supplement = TrackedSupplement(self.supplement_data)
        try:
            supplement.validate_data()
            validation_passed = True
        except:
            validation_passed = False
        
        self.assertTrue(validation_passed)
    
    def test_validate_data_missing_required_field(self):
        """Test validation with missing required field."""
        # Missing supplement_id
        data = self.supplement_data.copy()
        data.pop('supplementId')
        supplement = TrackedSupplement(data)
        
        with self.assertRaises(ValueError) as context:
            supplement.validate_data()
        
        self.assertTrue('Missing required field: supplement_id' in str(context.exception))
        
        # Missing dosage
        data = self.supplement_data.copy()
        data.pop('dosage')
        supplement = TrackedSupplement(data)
        
        with self.assertRaises(ValueError) as context:
            supplement.validate_data()
        
        self.assertTrue('Missing required field: dosage' in str(context.exception))


class TestTrackerSupplementList(unittest.TestCase):
    """Test case for the TrackerSupplementList model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_id = ObjectId()  # Use ObjectId instead of string
        self.supplement_data = {
            'supplementId': str(ObjectId()),
            'supplementName': 'Vitamin D',
            'dosage': 1000,
            'unit': 'mg',
            'frequency': 'daily',
            'duration': '30 days',
            'startDate': '2023-04-01T00:00:00',
            'endDate': '2023-05-01T00:00:00',
            'notes': 'Take with food',
            'createdAt': '2023-04-01T00:00:00',
            'updatedAt': '2023-04-01T00:00:00'
        }
        
    def test_init(self):
        """Test initialization of TrackerSupplementList."""
        data = {
            'user_id': self.user_id,
            'tracked_supplements': []
        }
        tracker_list = TrackerSupplementList(data)
        
        self.assertEqual(tracker_list.user_id, self.user_id)
        self.assertEqual(tracker_list.tracked_supplements, [])
    
    def test_get_supplement_names(self):
        """Test getting supplement names."""
        data = {
            'user_id': self.user_id,
            'tracked_supplements': [
                self.supplement_data,
                {**self.supplement_data, 'supplementName': 'Vitamin C'},
                {**self.supplement_data, 'supplementName': None}
            ]
        }
        tracker_list = TrackerSupplementList(data)
        
        names = tracker_list.get_supplement_names()
        
        self.assertEqual(len(names), 2)  # Only 2 have names
        self.assertIn('Vitamin D', names)
        self.assertIn('Vitamin C', names)
    
    @patch('app.models.tracker_supplement_list.get_db')
    def test_create_for_user(self, mock_get_db):
        """Test creating a TrackerSupplementList."""
        # Create a mock DB
        mock_db = MagicMock()
        # Return None for find_one (list doesn't exist yet)
        mock_db.TrackerSupplementList.find_one.return_value = None
        mock_db.TrackerSupplementList.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        mock_get_db.return_value = mock_db
        
        # Create a tracker supplement list
        tracker_list = TrackerSupplementList.create_for_user(str(self.user_id))
        
        # Check the DB was called correctly
        mock_db.TrackerSupplementList.insert_one.assert_called_once()
        
        # Check the returned object
        self.assertIsInstance(tracker_list, TrackerSupplementList)
        self.assertEqual(str(tracker_list.user_id), str(self.user_id))
    
    @patch('app.models.tracker_supplement_list.get_db')
    def test_create_failure(self, mock_get_db):
        """Test failure to create a TrackerSupplementList."""
        # Create a mock DB that returns an exception during insert
        mock_db = MagicMock()
        # Make sure find_one returns None (no existing list)
        mock_db.TrackerSupplementList.find_one.return_value = None
        mock_db.TrackerSupplementList.insert_one.side_effect = Exception("Database error")
        mock_get_db.return_value = mock_db
        
        # Try to create a tracker supplement list
        with self.assertRaises(Exception):
            TrackerSupplementList.create_for_user(str(self.user_id))
    
    @patch('app.models.tracker_supplement_list.get_db')
    def test_find_by_user_id(self, mock_get_db):
        """Test finding a TrackerSupplementList by user ID."""
        # Create a mock DB that returns a list
        mock_db = MagicMock()
        mock_db.TrackerSupplementList.find_one.return_value = {
            '_id': ObjectId(),
            'user_id': self.user_id,
            'tracked_supplements': []
        }
        mock_get_db.return_value = mock_db
        
        # Find a tracker supplement list
        tracker_list = TrackerSupplementList.find_by_user_id(str(self.user_id))
        
        # Check the returned object
        self.assertIsInstance(tracker_list, TrackerSupplementList)
        self.assertEqual(str(tracker_list.user_id), str(self.user_id))
    
    @patch('app.models.tracker_supplement_list.get_db')
    def test_find_by_user_id_not_found(self, mock_get_db):
        """Test finding a non-existent TrackerSupplementList."""
        # Create a mock DB that returns None
        mock_db = MagicMock()
        mock_db.TrackerSupplementList.find_one.return_value = None
        mock_get_db.return_value = mock_db
        
        # Try to find a tracker supplement list
        tracker_list = TrackerSupplementList.find_by_user_id(str(self.user_id))
        
        # Check the result is None
        self.assertIsNone(tracker_list)
    
    @patch('app.models.tracker_supplement_list.get_db')
    def test_add_tracked_supplement(self, mock_get_db):
        """Test adding a TrackedSupplement to the list."""
        # Create mock supplements and DB
        mock_db = MagicMock()
        
        # Initial find returns list
        mock_db.TrackerSupplementList.find_one.return_value = {
            '_id': ObjectId(),
            'user_id': self.user_id,
            'tracked_supplements': []
        }
        
        # After update, return updated list
        updated_list = {
            '_id': ObjectId(),
            'user_id': self.user_id,
            'tracked_supplements': [self.supplement_data]
        }
        
        # Setup find_one to return updated list the second time
        find_one_calls = 0
        def find_one_side_effect(*args, **kwargs):
            nonlocal find_one_calls
            if find_one_calls == 0:
                find_one_calls += 1
                return mock_db.TrackerSupplementList.find_one.return_value
            else:
                return updated_list
                
        mock_db.TrackerSupplementList.find_one.side_effect = find_one_side_effect
        mock_get_db.return_value = mock_db
        
        # Add a tracked supplement
        tracker_list = TrackerSupplementList.add_tracked_supplement(str(self.user_id), self.supplement_data)
        
        # Check the DB was updated
        mock_db.TrackerSupplementList.update_one.assert_called_once()
        
        # Check the returned object
        self.assertIsInstance(tracker_list, TrackerSupplementList)
        self.assertEqual(str(tracker_list.user_id), str(self.user_id))
    
    @patch('app.models.tracker_supplement_list.get_db')
    def test_delete_tracked_supplement(self, mock_get_db):
        """Test deleting a TrackedSupplement from the list."""
        # Create supplement ID
        supplement_id = str(ObjectId())
        
        # Create mock DB
        mock_db = MagicMock()
        
        # Initial list with the supplement
        initial_list = {
            '_id': ObjectId(),
            'user_id': self.user_id,
            'tracked_supplements': [{
                '_id': supplement_id,
                'supplementId': str(ObjectId()),
                'supplementName': 'Vitamin D'
            }]
        }
        
        # Updated list after deletion
        updated_list = {
            '_id': ObjectId(),
            'user_id': self.user_id,
            'tracked_supplements': []
        }
        
        # Setup find_one to return initial list then updated list
        find_one_calls = 0
        def find_one_side_effect(*args, **kwargs):
            nonlocal find_one_calls
            if find_one_calls == 0:
                find_one_calls += 1
                return initial_list
            else:
                return updated_list
                
        mock_db.TrackerSupplementList.find_one.side_effect = find_one_side_effect
        mock_get_db.return_value = mock_db
        
        # Delete a tracked supplement
        tracker_list = TrackerSupplementList.delete_tracked_supplement(str(self.user_id), supplement_id)
        
        # Check the DB was updated
        mock_db.TrackerSupplementList.update_one.assert_called_once()
        
        # Check the returned object
        self.assertIsInstance(tracker_list, TrackerSupplementList)
        self.assertEqual(str(tracker_list.user_id), str(self.user_id))
    
    @patch('app.models.tracker_supplement_list.get_db')
    def test_update_tracked_supplement(self, mock_get_db):
        """Test updating a TrackedSupplement in the list."""
        # Create supplement ID and updated data
        supplement_id = str(ObjectId())
        updated_data = self.supplement_data.copy()
        updated_data['_id'] = supplement_id
        updated_data['dosage'] = 2000
        
        # Create mock DB
        mock_db = MagicMock()
        
        # Initial list with the supplement
        initial_list = {
            '_id': ObjectId(),
            'user_id': self.user_id,
            'tracked_supplements': [{
                '_id': supplement_id,
                'supplementId': str(ObjectId()),
                'supplementName': 'Vitamin D',
                'dosage': 1000
            }]
        }
        
        # Updated list after update
        updated_list = {
            '_id': ObjectId(),
            'user_id': self.user_id,
            'tracked_supplements': [{
                '_id': supplement_id,
                'supplementId': str(ObjectId()),
                'supplementName': 'Vitamin D',
                'dosage': 2000
            }]
        }
        
        # Setup find_one to return initial list then updated list
        find_one_calls = 0
        def find_one_side_effect(*args, **kwargs):
            nonlocal find_one_calls
            if find_one_calls == 0:
                find_one_calls += 1
                return initial_list
            else:
                return updated_list
                
        mock_db.TrackerSupplementList.find_one.side_effect = find_one_side_effect
        mock_get_db.return_value = mock_db
        
        # Update a tracked supplement
        tracker_list = TrackerSupplementList.update_tracked_supplement(str(self.user_id), supplement_id, updated_data)
        
        # Check the DB was updated
        mock_db.TrackerSupplementList.update_one.assert_called_once()
        
        # Check the returned object
        self.assertIsInstance(tracker_list, TrackerSupplementList)
        self.assertEqual(str(tracker_list.user_id), str(self.user_id))