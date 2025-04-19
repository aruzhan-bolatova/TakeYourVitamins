from app.models.user import User
from app.models.supplement import Supplement
from app.models.intake_log import IntakeLog
from app.models.symptom_log import SymptomLog
from app.models.interaction import Interaction
from app.models.tracker_supplement_list import TrackerSupplementList

from app.db.db import get_database as get_db
import logging

logger = logging.getLogger(__name__)

def init_indexes():
    """
    Initialize all collection indexes for MongoDB.
    This should be called during application startup.
    """
    User.create_indexes()
    Supplement.create_indexes()
    IntakeLog.create_indexes()
    SymptomLog.create_indexes()
    Interaction.create_indexes()
    TrackerSupplementList.create_indexes()
    
    print("MongoDB indexes created successfully.")

def init_db():
    """Initialize the database collections and indexes."""
    logger.info("Initializing database...")
    db = get_db()
    
    # Create collections if they don't exist
    if 'Users' not in db.list_collection_names():
        db.create_collection('Users')
        db.Users.create_index('email', unique=True)
        db.Users.create_index('userId', unique=True)
        logger.info("Created Users collection and indexes")
    
    # Create TokenBlacklist collection if it doesn't exist
    if 'TokenBlacklist' not in db.list_collection_names():
        db.create_collection('TokenBlacklist')
        db.TokenBlacklist.create_index('jti', unique=True)
        # Add expiration index for automatic cleanup
        db.TokenBlacklist.create_index('expiresAt', expireAfterSeconds=0)
        logger.info("Created TokenBlacklist collection and indexes")
        
    # Create Tracker Supplement List collection if it doesn't exist
    if 'TrackerSupplementList' not in db.list_collection_names():
        db.create_collection('TrackerSupplementList')
        db.TrackerSupplementList.create_index('userId', unique=True)
        logger.info("Created TrackerSupplementList collection and indexes")
        
    # Create other collections if they don't exist
    if 'Supplements' not in db.list_collection_names():
        db.create_collection('Supplements')
        db.Supplements.create_index('name', unique=True)
        logger.info("Created Supplements collection and indexes")
    
    if 'IntakeLogs' not in db.list_collection_names():
        db.create_collection('IntakeLogs')
        db.IntakeLogs.create_index('userId')
        db.IntakeLogs.create_index('trackedSupplementId')
        logger.info("Created IntakeLogs collection and indexes")
    
    logger.info("Database initialization complete") 