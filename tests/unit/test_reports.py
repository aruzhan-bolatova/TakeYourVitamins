import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# Add the parent directory to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.user import User
from app.models.intake_log import IntakeLog
from app.models.symptom_log import SymptomLog
from app.models.supplement import Supplement
from app.routes.reports import (
    _generate_intake_summary,
    _generate_symptom_summary,
    _analyze_correlations,
    _calculate_streaks,
    _calculate_progress,
    _generate_recommendations
)


if __name__ == '__main__':
    unittest.main() 