from app.db.db import get_database as get_db
from app.db.utils import hash_password, check_password
from datetime import datetime, timezone
import re

class User:
    def __init__(self, user_data: dict):
        self._id = user_data.get('_id')
        self.user_id = user_data.get('userId')
        self.name = user_data.get('name')
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.age = user_data.get('age')
        self.gender = user_data.get('gender')
        self.role = user_data.get('role', 'user')  # Default role is 'user'
        self.created_at = user_data.get('createdAt')
        self.updated_at = user_data.get('updatedAt')
        self.deleted_at = user_data.get('deletedAt')
        
        
    def to_dict(self) -> dict:
        """
        Convert the User object to a dictionary for database operations.
        """
        return {
            '_id': str(self._id) if self._id else None,
            'userId': self.user_id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'age': self.age,
            'gender': self.gender,
            'role': self.role,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
            'deletedAt': self.deleted_at,
        }

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format using a regex pattern.
        Returns True if the email is valid, False otherwise.
        """
        # More comprehensive email validation regex pattern
        # This pattern rejects emails with double periods in the domain
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_email_unique(email: str, exclude_user_id: str = None) -> bool:
        """
        Check if an email is unique in the database.
        
        Args:
            email: The email to check
            exclude_user_id: Optional user ID to exclude from the check (for updates)
        
        Returns:
            bool: True if the email is unique, False otherwise
        """
        db = get_db()
        query = {'email': email, 'deletedAt': None}
        
        # If exclude_user_id is provided, exclude that user from the check
        if exclude_user_id:
            query['_id'] = {'$ne': exclude_user_id}
            
        existing_user = db.Users.find_one(query)
        return existing_user is None

    @staticmethod
    def create(name: str, email: str, password: str, age: int, gender: str, role: str = 'user'):
        # Validate email format
        if not User.validate_email(email):
            raise ValueError('Invalid email format')
            
        db = get_db()
        # Check if email already exists
        if not User.is_email_unique(email):
            raise ValueError('Email already exists')
        
        
        user_id = f"USER{str(datetime.now(timezone.utc).timestamp()).replace('.', '')}"
        user = {
            'userId': user_id,
            'name': name,
            'email': email,
            'password': hash_password(password),
            'age': age,
            'gender': gender,
            'role': role,  # Store the role
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'updatedAt': None,
            'deletedAt': None
        }
        result = db.Users.insert_one(user)
        user['_id'] = result.inserted_id
        return User(user)

    @staticmethod
    def authenticate(email: str, password: str):
        db = get_db()
        user = db.Users.find_one({'email': email, 'deletedAt': None})  # Only active users can authenticate
        if not user or not check_password(password, user['password']):
            return None
        return User(user)

    @staticmethod
    def find_by_id(_id: str):
        print(f"User ID received: {_id}")
        db = get_db()
        user = db.Users.find_one({'_id': _id, 'deletedAt': None})
        print(f"User found: {user}")
        return User(user) if user else None

    @staticmethod
    def update(_id: str, data: dict):
        db = get_db()
        user = db.Users.find_one({'_id': _id, 'deletedAt': None})
        if not user:
            return None
        
        # Fields that can be updated
        allowed_fields = ['name', 'age', 'gender', 'email']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        # Validate and check email uniqueness if being updated
        if 'email' in update_data:
            # Validate email format
            if not User.validate_email(update_data['email']):
                raise ValueError('Invalid email format')
                
            # Check if new email is unique (excluding current user)
            if not User.is_email_unique(update_data['email'], _id):
                raise ValueError('Email already exists')
        
        # Handle password separately for security
        if 'password' in data and data['password']:
            update_data['password'] = hash_password(data['password'])
        
        if update_data:
            update_data['updatedAt'] = datetime.now(timezone.utc).isoformat()
            db.Users.update_one(
                {'_id': _id},
                {'$set': update_data}
            )
        
        # Get updated user data
        updated_user = db.Users.find_one({'_id': _id})
        return User(updated_user)

    @staticmethod
    def delete(_id: str):
        db = get_db()
        user = db.Users.find_one({'_id': _id, 'deletedAt': None})
        if not user:
            return None
        
        db.IntakeLogs.delete_many({'user_id': _id})
        db.SymptomLogs.delete_many({'user_id': _id})
        db.TrackerSupplementList.delete_one({'user_id': _id})
        db.Users.delete_one({'_id': _id})
        
        return _id