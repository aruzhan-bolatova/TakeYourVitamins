import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
from datetime import datetime
from bson.objectid import ObjectId

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app

if __name__ == '__main__':
    unittest.main()
