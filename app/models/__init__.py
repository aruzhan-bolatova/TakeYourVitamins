from app.db.db import get_database as get_db
from app.models.user import User
from app.models.supplement import Supplement
from app.models.intake_log import IntakeLog
from app.models.symptom_log import SymptomLog
from app.models.interaction import Interaction
from app.models.token_blacklist import TokenBlacklist
from app.models.init_db import init_db

__all__ = [
    'User', 'Supplement', 'IntakeLog', 'SymptomLog', 
    'Interaction', 'TokenBlacklist', 'init_db'
]

def init_db():
    db = get_db()
    db.Users.create_index('userId', unique=True)
    db.Users.create_index('email', unique=True)
    db.Supplements.create_index('supplementId', unique=True)
    db.Supplements.create_index('name', unique=True)
    db.IntakeLogs.create_index('intakeLogId', unique=True)
    db.SymptomLogs.create_index('symptomLogId', unique=True)
    db.Interactions.create_index('interactionId', unique=True)