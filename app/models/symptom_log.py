from app.db.db import get_database as get_db
from bson.objectid import ObjectId
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any, Union
import uuid

class SymptomLog:
    SEVERITY_LEVELS = ["none", "mild", "average", "severe"]
    REQUIRED_FIELDS = ['user_id', 'symptom_id', 'date', 'severity']
    
    def __init__(self, symptom_log_data: dict):
        self._id = symptom_log_data.get('_id')
        self.user_id = symptom_log_data.get('user_id')
        self.symptom_id = symptom_log_data.get('symptom_id')
        self.date = symptom_log_data.get('date')
        self.severity = symptom_log_data.get('severity', 'average')
        self.notes = symptom_log_data.get('notes', '')
        self.created_at = symptom_log_data.get('created_at')
        self.updated_at = symptom_log_data.get('updated_at')
        self.deleted_at = symptom_log_data.get('deleted_at')
    
    def to_dict(self) -> Dict:
        """Convert symptom log to dictionary"""
        return {
            "_id": str(self._id) if self._id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "symptom_id": str(self.symptom_id) if self.symptom_id else None,
            "date": self.date,
            "severity": self.severity,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at
        }
    
    def validate_data(self):
        """Validate the symptom log data"""
        for field in self.REQUIRED_FIELDS:
            if not getattr(self, field):
                raise ValueError(f"Missing required field: {field}")
        
        # Validate severity
        if self.severity not in self.SEVERITY_LEVELS:
            raise ValueError(f"Severity must be one of {self.SEVERITY_LEVELS}")

    @staticmethod
    def create(symptom_log_data: dict):
        """Create a new symptom log"""
        # Validate data
        if not symptom_log_data:
            raise ValueError("Symptom log data is required")

        db = get_db()
        
        # Prepare the symptom log data
        now = datetime.now(timezone.utc).isoformat()
        
        # Default values
        symptom_log_data['notes'] = symptom_log_data.get('notes', '')
        
        # Convert string IDs to ObjectId
        if isinstance(symptom_log_data.get('user_id'), str):
            symptom_log_data['user_id'] = ObjectId(symptom_log_data['user_id'])
            
        if isinstance(symptom_log_data.get('symptom_id'), str):
            symptom_log_data['symptom_id'] = ObjectId(symptom_log_data['symptom_id'])
        
        symptom_log_data['symptomLogId'] = symptom_log_data.get('symptomLogId', str(uuid.uuid4()))
        # Add timestamps
        symptom_log_data['created_at'] = now
        symptom_log_data['updated_at'] = now
        symptom_log_data['deleted_at'] = None
        
        # Create object and validate
        symptom_log = SymptomLog(symptom_log_data)
        symptom_log.validate_data()
        
        # Check if a log already exists for this user, symptom, and date
        existing_log = db.SymptomLogs.find_one({
            "user_id": symptom_log_data['user_id'],
            "symptom_id": symptom_log_data['symptom_id'],
            "date": symptom_log_data['date'],
            "deleted_at": None
        })
        
        if existing_log:
            # Update existing log
            update_dict = {
                "severity": symptom_log_data['severity'],
                "notes": symptom_log_data['notes'],
                "updated_at": now
            }
            db.SymptomLogs.update_one(
                {"_id": existing_log["_id"]},
                {"$set": update_dict}
            )
            # Return the updated log
            updated_log = db.SymptomLogs.find_one({"_id": existing_log["_id"]})
            return SymptomLog(updated_log)
        else:
            # Insert into database
            result = db.SymptomLogs.insert_one(symptom_log_data)
            
            if not result.inserted_id:
                raise ValueError("Failed to create symptom log")
                
            # Get the created symptom log with its ID
            created_log = db.SymptomLogs.find_one({"_id": result.inserted_id})
            return SymptomLog(created_log)

    @staticmethod
    def find_by_id(log_id: str):
        """Find a symptom log by ID"""
        db = get_db()
        try:
            if isinstance(log_id, str):
                log_id = ObjectId(log_id)
                
            symptom_log = db.SymptomLogs.find_one({'_id': log_id, 'deleted_at': None})
            return SymptomLog(symptom_log) if symptom_log else None
        except Exception as e:
            raise ValueError(f"Error finding symptom log: {e}")

    @staticmethod
    def find_by_user_id(user_id: str):
        """Find all symptom logs for a user"""
        db = get_db()
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
                
            SymptomLogs = db.SymptomLogs.find({'user_id': user_id, 'deleted_at': None})
            return [SymptomLog(log) for log in SymptomLogs]
        except Exception as e:
            raise ValueError(f"Error finding symptom logs: {e}")

    @staticmethod
    def find_by_date(user_id: str, date: str):
        """Find all symptom logs for a user on a specific date"""
        db = get_db()
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
                
            SymptomLogs = db.SymptomLogs.find({
                'user_id': user_id,
                'date': date,
                'deleted_at': None
            })
            return [SymptomLog(log) for log in SymptomLogs]
        except Exception as e:
            raise ValueError(f"Error finding symptom logs for date: {e}")

    @staticmethod
    def find_active_symptoms_for_date(user_id: str, date: str):
        """Find all active symptom logs (severity not 'none') for a user on a specific date"""
        db = get_db()
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
                
            SymptomLogs = db.SymptomLogs.find({
                'user_id': user_id,
                'date': date,
                'severity': {'$ne': 'none'},
                'deleted_at': None
            })
            return [SymptomLog(log) for log in SymptomLogs]
        except Exception as e:
            raise ValueError(f"Error finding active symptoms for date: {e}")

    @staticmethod
    def find_by_date_range(user_id: str, start_date: str, end_date: str):
        """Find symptom logs within a date range for a user"""
        db = get_db()
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
                
            SymptomLogs = db.SymptomLogs.find({
                'user_id': user_id,
                'date': {'$gte': start_date, '$lte': end_date},
                'deleted_at': None
            })
            return [SymptomLog(log) for log in SymptomLogs]
        except Exception as e:
            raise ValueError(f"Error finding symptom logs by date range: {e}")

    @staticmethod
    def get_dates_with_symptoms(user_id: str):
        """Get all dates where a user has logged active symptoms"""
        db = get_db()
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
                
            pipeline = [
                {"$match": {"user_id": user_id, "severity": {"$ne": "none"}, "deleted_at": None}},
                {"$group": {"_id": "$date"}},
                {"$sort": {"_id": 1}}
            ]
            
            result = db.SymptomLogs.aggregate(pipeline)
            return [doc["_id"] for doc in result]
        except Exception as e:
            raise ValueError(f"Error finding dates with symptoms: {e}")

    @staticmethod
    def update(log_id: str, update_data: dict):
        """Update a symptom log"""
        db = get_db()
        try:
            # Find the log first
            if isinstance(log_id, str):
                log_id = ObjectId(log_id)
                
            existing_log = db.SymptomLogs.find_one({'_id': log_id, 'deleted_at': None})
            if not existing_log:
                raise ValueError("Symptom log not found")
            
            # Update only allowed fields
            allowed_fields = ['severity', 'notes']
            update_dict = {k: v for k, v in update_data.items() if k in allowed_fields}
            
            if update_dict:
                update_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
                db.SymptomLogs.update_one(
                    {'_id': log_id},
                    {'$set': update_dict}
                )
            
            # Return the updated log
            updated_log = db.SymptomLogs.find_one({'_id': log_id})
            return SymptomLog(updated_log)
        except Exception as e:
            raise ValueError(f"Error updating symptom log: {e}")

    @staticmethod
    def delete(log_id: str):
        """Soft delete a symptom log"""
        print(f"[DEBUG] Attempting to delete symptom log with ID: {log_id}")
        db = get_db()
        try:
            # Convert string ID to ObjectId
            if isinstance(log_id, str):
                try:
                    log_id = ObjectId(log_id)
                except Exception as e:
                    print(f"[ERROR] Failed to convert log_id to ObjectId: {e}")
                                
            # Find the log first
            existing_log = db.SymptomLogs.find_one({'_id': log_id, 'deleted_at': None})
            if not existing_log:
                raise ValueError("Symptom log not found")
            
            # Soft delete by setting deleted_at
            now = datetime.now(timezone.utc).isoformat()
            db.SymptomLogs.update_one(
                {'_id': log_id},
                {'$set': {
                    'deleted_at': now,
                    'updated_at': now
                }}
            )
            return True
        except Exception as e:
            raise ValueError(f"Error deleting symptom log: {e}")

    @staticmethod
    def get_symptom_details():
        """Get all symptoms with their categories"""
        db = get_db()
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "SymptomCategories",
                        "localField": "categoryId",
                        "foreignField": "_id",
                        "as": "category"
                    }
                },
                {
                    "$unwind": "$category"
                },
                {
                    "$project": {
                        "_id": 1,
                        "name": 1,
                        "icon": 1,
                        "categoryId": 1,
                        "categoryName": "$category.name",
                        "categoryIcon": "$category.icon"
                    }
                }
            ]
            
            symptoms = list(db.Symptoms.aggregate(pipeline))
            return {str(symptom["_id"]): symptom for symptom in symptoms}
        except Exception as e:
            raise ValueError(f"Error getting symptom details: {e}")

    @staticmethod
    def get_symptoms_summary(user_id: str, date: str):
        """Get a summary of symptoms by category for a specific date"""
        db = get_db()
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
                
            # Get active logs
            active_logs = db.SymptomLogs.find({
                'user_id': user_id,
                'date': date,
                'severity': {'$ne': 'none'},
                'deleted_at': None
            })
            
            # Get symptom details
            symptoms = SymptomLog.get_symptom_details()
            
            # Group by category
            categories = {
                "general": {"name": "General", "icon": "🔍", "symptoms": []},
                "mood": {"name": "Mood", "icon": "😊", "symptoms": []},
                "sleep": {"name": "Sleep", "icon": "😴", "symptoms": []},
                "digestive": {"name": "Digestive", "icon": "🍽️", "symptoms": []},
                "appetite": {"name": "Appetite", "icon": "🥑", "symptoms": []},
                "activity": {"name": "Physical Activity", "icon": "🏃‍♀️", "symptoms": []}
            }
            
            # Parse notes from any log
            notes = ""
            for log in active_logs:
                if log.get('notes'):
                    notes = log['notes']
                    break
            
            # Reset cursor
            active_logs = db.SymptomLogs.find({
                'user_id': user_id,
                'date': date,
                'severity': {'$ne': 'none'},
                'deleted_at': None
            })
            
            # Populate categories with symptoms
            for log in active_logs:
                symptom_id = str(log['symptom_id'])
                if symptom_id in symptoms:
                    symptom_info = symptoms[symptom_id]
                    category_name = symptom_info['categoryName'].lower()
                    
                    # Map category name to id if needed
                    category_id = ""
                    if "general" in category_name:
                        category_id = "general"
                    elif "mood" in category_name:
                        category_id = "mood"
                    elif "sleep" in category_name:
                        category_id = "sleep"
                    elif "digestive" in category_name:
                        category_id = "digestive"
                    elif "appetite" in category_name:
                        category_id = "appetite"
                    elif "activity" in category_name or "physical" in category_name:
                        category_id = "activity"
                    
                    if category_id in categories:
                        categories[category_id]["symptoms"].append({
                            "id": symptom_id,
                            "name": symptom_info['name'],
                            "icon": symptom_info['icon'],
                            "severity": log['severity']
                        })
            
            # Filter out empty categories
            summary = {
                "categories": [cat for cat in categories.values() if cat["symptoms"]],
                "notes": notes,
                "date": date
            }
            
            return summary
        except Exception as e:
            raise ValueError(f"Error getting symptoms summary: {e}")


class SymptomCategoryManager:
    @staticmethod
    def initialize_symptom_data():
        """Initialize the database with symptom categories and symptoms if it's empty"""
        db = get_db()
        
        # Only initialize if symptom_categories collection is empty
        if db.SymptomCategories.count_documents({}) == 0:
            print("[DEBUG] Initializing symptom categories and symptoms...")
            # Create symptom categories
            categories = [
                {"name": "General", "id": "general", "icon": "🔍"},
                {"name": "Mood", "id": "mood", "icon": "😊"},
                {"name": "Sleep", "id": "sleep", "icon": "😴"},
                {"name": "Digestive", "id": "digestive", "icon": "🍽️"},
                {"name": "Appetite", "id": "appetite", "icon": "🥑"},
                {"name": "Physical Activity", "id": "activity", "icon": "🏃‍♀️"}
            ]
            
            # Insert categories
            category_ids = {}
            for category in categories:
                result = db.SymptomCategories.insert_one(category)
                category_ids[category["id"]] = result.inserted_id
                print(f"[DEBUG] Inserted category: {category['name']} with ID: {result.inserted_id}")
            
            # Define symptoms for each category
            symptoms = [
                # General
                {"name": "Everything is fine", "icon": "👍", "categoryId": category_ids["general"]},
                {"name": "Skin issues", "icon": "🤡", "categoryId": category_ids["general"]},
                {"name": "Fatigue", "icon": "🫠", "categoryId": category_ids["general"]},
                {"name": "Headache", "icon": "🤕", "categoryId": category_ids["general"]},
                {"name": "Abdominal Pain", "icon": "😣", "categoryId": category_ids["general"]},
                {"name": "Dizziness", "icon": "😵‍💫", "categoryId": category_ids["general"]},
                
                # Mood
                {"name": "Calm", "icon": "😌", "categoryId": category_ids["mood"]},
                {"name": "Mood swings", "icon": "🔄", "categoryId": category_ids["mood"]},
                {"name": "Happy", "icon": "😊", "categoryId": category_ids["mood"]},
                {"name": "Energetic", "icon": "⚡", "categoryId": category_ids["mood"]},
                {"name": "Irritated", "icon": "🥴", "categoryId": category_ids["mood"]},
                {"name": "Depressed", "icon": "😓", "categoryId": category_ids["mood"]},
                {"name": "Low energy", "icon": "🥱", "categoryId": category_ids["mood"]},
                {"name": "Anxious", "icon": "😰", "categoryId": category_ids["mood"]},
                
                # Sleep
                {"name": "Insomnia", "icon": "😳", "categoryId": category_ids["sleep"]},
                {"name": "Good sleep", "icon": "😴", "categoryId": category_ids["sleep"]},
                {"name": "Restless", "icon": "🔄", "categoryId": category_ids["sleep"]},
                {"name": "Tired", "icon": "🥱", "categoryId": category_ids["sleep"]},
                
                # Digestive
                {"name": "Bloating", "icon": "🎈", "categoryId": category_ids["digestive"]},
                {"name": "Nausea", "icon": "🤢", "categoryId": category_ids["digestive"]},
                {"name": "Constipation", "icon": "⏸️", "categoryId": category_ids["digestive"]},
                {"name": "Diarrhea", "icon": "⏩", "categoryId": category_ids["digestive"]},
                
                # Appetite
                {"name": "Low", "icon": "🫢", "categoryId": category_ids["appetite"]},
                {"name": "Normal", "icon": "🍽️", "categoryId": category_ids["appetite"]},
                {"name": "High", "icon": "🍔", "categoryId": category_ids["appetite"]},
                
                # Physical Activity
                {"name": "Didn't exercise", "icon": "⭕️", "categoryId": category_ids["activity"]},
                {"name": "Yoga", "icon": "🧘‍♀️", "categoryId": category_ids["activity"]},
                {"name": "Gym", "icon": "🏋️", "categoryId": category_ids["activity"]},
                {"name": "Swimming", "icon": "🏊‍♀️", "categoryId": category_ids["activity"]},
                {"name": "Running", "icon": "🏃", "categoryId": category_ids["activity"]},
                {"name": "Cycling", "icon": "🚴‍♀️", "categoryId": category_ids["activity"]},
                {"name": "Team Sports", "icon": "⛹️‍♀️", "categoryId": category_ids["activity"]},
                {"name": "Aerobics/Dancing", "icon": "💃", "categoryId": category_ids["activity"]}
            ]
            
            
            # Insert symptoms
            for symptom in symptoms:
                symptom["symptomId"] = symptom["name"].lower().replace(" ", "_")
                # Insert into database
                result = db.Symptoms.insert_one(symptom)
                print(f"[DEBUG] Inserted symptom: {symptom['name']} with ID: {result.inserted_id}")
            
            
        else:
            print("[DEBUG] Symptom categories and symptoms already initialized: ", db.SymptomCategories.count_documents({}))
