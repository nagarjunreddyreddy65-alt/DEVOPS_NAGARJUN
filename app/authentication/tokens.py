import hashlib
import time
import secrets
from typing import Dict, Optional

class TokenManager:
    """Manages authentication tokens, validation, and session expirations."""
    
    def __init__(self, secret_key: str = "super-secret-key", token_ttl: int = 3600):
        self.secret_key = secret_key
        self.token_ttl = token_ttl
        self.active_sessions: Dict[str, dict] = {}
        
    def generate_token(self, username: str) -> str:
        entropy = secrets.token_hex(16)
        raw = f"{username}:{time.time()}:{entropy}:{self.secret_key}".encode()
        token = hashlib.sha256(raw).hexdigest()
        self.active_sessions[token] = {
            "username": username,
            "created_at": time.time(),
            "expires_at": time.time() + self.token_ttl
        }
        return token
        
    def validate_token(self, token: str) -> bool:
        session = self.active_sessions.get(token)
        if not session:
            return False
        if time.time() > session["expires_at"]:
            del self.active_sessions[token]
            return False
        return True

    def revoke_token(self, token: str) -> bool:
        if token in self.active_sessions:
            del self.active_sessions[token]
            return True
        return False
        
    def get_user_for_token(self, token: str) -> Optional[str]:
        if self.validate_token(token):
            return self.active_sessions[token]["username"]
        return None
