# Collection names
USERS_COLLECTION = "Users"
SUPPLEMENTS_COLLECTION = "Supplements"
INTAKE_LOGS_COLLECTION = "IntakeLogs"
SYMPTOM_LOGS_COLLECTION = "SymptomLogs"
INTERACTIONS_COLLECTION = "Interactions"

# Schema fields for each collection
USER_FIELDS = {
    "USER_ID": "userId",
    "NAME": "name",
    "EMAIL": "email",
    "AGE": "age",
    "GENDER": "gender",
    "PASSWORD": "password",
    "CREATED_AT": "createdAt",
    "UPDATED_AT": "updatedAt",
    "DELETED_AT": "deletedAt"
}

SUPPLEMENT_FIELDS = {
    "SUPPLEMENT_ID": "supplementId",
    "NAME": "name",
    "ALIASES": "aliases",
    "DESCRIPTION": "description",
    "INTAKE_PRACTICES": "intakePractices",
    "INTAKE_PRACTICES_DOSAGE": "intakePractices.dosage",
    "INTAKE_PRACTICES_TIMING": "intakePractices.timing",
    "INTAKE_PRACTICES_SPECIAL_INSTRUCTIONS": "intakePractices.specialInstructions",
    "SCIENTIFIC_DETAILS": "scientificDetails",
    "CATEGORY": "category",
    "UPDATED_AT": "updatedAt"
}

INTAKE_LOG_FIELDS = {
    "INTAKE_LOG_ID": "intakeLogId",
    "USER_ID": "userId",
    "SUPPLEMENT_ID": "supplementId",
    "INTAKE_DATE": "intakeDate",
    "INTAKE_TIME": "intakeTime",
    "DOSAGE": "dosage",
    "NOTES": "notes",
    "CREATED_AT": "createdAt",
    "UPDATED_AT": "updatedAt",
    "IS_DELETED": "isDeleted"
}

SYMPTOM_LOG_FIELDS = {
    "SYMPTOM_LOG_ID": "symptomLogId",
    "USER_ID": "userId",
    "SYMPTOM": "symptom",
    "RATING": "rating",
    "LOG_DATE": "logDate",
    "COMMENTS": "comments",
    "INTAKE_LOG_ID": "intakeLogId",
    "CREATED_AT": "createdAt",
    "UPDATED_AT": "updatedAt"
}

INTERACTION_FIELDS = {
    "INTERACTION_ID": "interactionId",
    "SUPPLEMENT_ID1": "supplementId1",
    "SUPPLEMENT_ID2": "supplementId2",
    "FOOD_ITEM": "foodItem",
    "INTERACTION_TYPE": "interactionType",
    "EFFECT": "effect",
    "DESCRIPTION": "description",
    "SEVERITY": "severity",
    "RECOMMENDATION": "recommendation",
    "SOURCES": "sources",
    "UPDATED_AT": "updatedAt"
}