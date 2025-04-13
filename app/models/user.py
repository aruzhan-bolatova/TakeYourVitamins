from app.db.db import get_database as get_db
from app.db.utils import hash_password, check_password
from datetime import datetime, timezone

class User:
    def __init__(self, user_data: dict):
        self.user_id = user_data.get('userId')
        self.name = user_data.get('name')
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.age = user_data.get('age')
        self.gender = user_data.get('gender')
        self.created_at = user_data.get('createdAt')
        self.updated_at = user_data.get('updatedAt')
        self.deleted_at = user_data.get('deletedAt')

    @staticmethod
    def create(name: str, email: str, password: str, age: int, gender: str):
        db = get_db()
        if db.Users.find_one({'email': email}):
            raise ValueError('Email already exists')
        user_id = f"USER{str(datetime.now(timezone.utc).timestamp()).replace('.', '')}"
        user = {
            'userId': user_id,
            'name': name,
            'email': email,
            'password': hash_password(password),
            'age': age,
            'gender': gender,
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'updatedAt': None,
            'deletedAt': None
        }
        db.Users.insert_one(user)
        return User(user)

    @staticmethod
    def authenticate(email: str, password: str):
        db = get_db()
        user = db.Users.find_one({'email': email})
        if not user or not check_password(password, user['password']):
            return None
        return User(user)

    @staticmethod
    def find_by_id(user_id: str):
        db = get_db()
        user = db.Users.find_one({'userId': user_id})
        return User(user) if user else None