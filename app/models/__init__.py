# Import the database connection function
from app.db.db import get_database as get_db

# Import model classes
from app.models.user import User
from app.models.supplement import Supplement
from app.models.intake_log import IntakeLog
from app.models.symptom_log import SymptomLog
from app.models.interaction import Interaction
from app.models.token_blacklist import TokenBlacklist

# Import the database initialization function
from app.models.init_db import init_db

# Define the public API of this module
# These are the symbols that will be exposed when using `from app.models import *`
__all__ = [
    'User', 'Supplement', 'IntakeLog', 'SymptomLog', 
    'Interaction', 'TokenBlacklist', 'init_db', 'Symptoms', 'SymptomCategories', 
]

# Note: Database initialization is handled in app/models/init_db.py
# This prevents duplicate init_db function definitions
    