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
    'Interaction', 'TokenBlacklist', 'init_db'
]

# Function to initialize database indexes
def init_db():
    # Get the database connection
    db = get_db()
    
    # Create unique indexes for the Users collection
    db.Users.create_index('userId', unique=True)  # Ensure userId is unique
    db.Users.create_index('email', unique=True)  # Ensure email is unique
    
    # Create unique indexes for the Supplements collection
    db.Supplements.create_index('supplementId', unique=True)  # Ensure supplementId is unique
    db.Supplements.create_index('name', unique=True)  # Ensure name is unique
    
    # Create unique indexes for the IntakeLogs collection
    db.IntakeLogs.create_index('intakeLogId', unique=True)  # Ensure intakeLogId is unique
    
    # Create unique indexes for the SymptomLogs collection
    db.SymptomLogs.create_index('symptomLogId', unique=True)  # Ensure symptomLogId is unique
    
    # Create unique indexes for the Interactions collection
    db.Interactions.create_index('interactionId', unique=True)  # Ensure interactionId is unique