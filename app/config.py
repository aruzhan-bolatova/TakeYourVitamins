import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app configuration
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'development-key')

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'tyv')

# JWT configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'development-jwt-key')
