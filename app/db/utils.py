import bcrypt
from datetime import datetime
import time

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Args:
        password (str): The plaintext password to hash.
    Returns:
        str: The hashed password.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """
    Check if a plaintext password matches a hashed password.
    Args:
        password (str): The plaintext password to check.
        hashed (str): The hashed password to compare against.
    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_unique_id(prefix: str) -> str:
    """
    Generate a unique ID with a given prefix.
    Args:
        prefix (str): The prefix for the ID (e.g., 'INTAKE', 'SYMPTOM').
    Returns:
        str: A unique ID in the format <prefix><timestamp>.
    """
    timestamp = str(time.time()).replace('.', '')
    return f"{prefix}{timestamp}"

def validate_date(date_str: str, date_format: str = "%Y-%m-%d") -> bool:
    """
    Validate a date string against a specified format.
    Args:
        date_str (str): The date string to validate (e.g., '2025-04-13').
        date_format (str): The expected date format (default: '%Y-%m-%d').
    Returns:
        bool: True if the date is valid, False otherwise.
    """
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False