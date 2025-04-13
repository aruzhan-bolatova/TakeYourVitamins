from app.db.db import get_database as get_db

def init_db():
    db = get_db()
    db.Users.create_index('userId', unique=True)
    db.Users.create_index('email', unique=True)
    db.Supplements.create_index('supplementId', unique=True)
    db.Supplements.create_index('name', unique=True)
    db.IntakeLogs.create_index('intakeLogId', unique=True)
    db.SymptomLogs.create_index('symptomLogId', unique=True)
    db.Interactions.create_index('interactionId', unique=True)