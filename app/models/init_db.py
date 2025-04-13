from app.models.user import User
from app.models.supplement import Supplement
from app.models.intake_log import IntakeLog
from app.models.symptom_log import SymptomLog
from app.models.interaction import Interaction

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
    
    print("MongoDB indexes created successfully.") 