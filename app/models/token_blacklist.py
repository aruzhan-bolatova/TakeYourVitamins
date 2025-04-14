from app.db.db import get_database as get_db
from datetime import datetime, timezone

class TokenBlacklist:
    def __init__(self, token_data: dict):
        self.jti = token_data.get('jti')
        self.token_type = token_data.get('type')
        self.user_id = token_data.get('userId')
        self.revoked_at = token_data.get('revokedAt')
        self.expires_at = token_data.get('expiresAt')

    @staticmethod
    def add_to_blacklist(jti: str, token_type: str, user_id: str, expires_at: datetime):
        """
        Add a token to the blacklist
        Args:
            jti: The JWT ID
            token_type: The token type (access or refresh)
            user_id: The ID of the user the token belongs to
            expires_at: When the token expires
        """
        db = get_db()
        token = {
            'jti': jti,
            'type': token_type,
            'userId': user_id,
            'revokedAt': datetime.now(timezone.utc).isoformat(),
            'expiresAt': expires_at.isoformat() if expires_at else None
        }
        db.TokenBlacklist.insert_one(token)
        return TokenBlacklist(token)

    @staticmethod
    def is_blacklisted(jti: str) -> bool:
        """
        Check if a token is blacklisted
        Args:
            jti: The JWT ID to check
        Returns:
            bool: True if the token is blacklisted, False otherwise
        """
        db = get_db()
        token = db.TokenBlacklist.find_one({'jti': jti})
        return token is not None 