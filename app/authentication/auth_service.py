import hashlib
from typing import Dict, Optional, Tuple
from .tokens import TokenManager

class AuthService:
    """Authentication and user management service."""
    
    def __init__(self, token_manager: Optional[TokenManager] = None):
        self.token_manager = token_manager or TokenManager()
        self.users: Dict[str, dict] = {}
        # Prepopulate demo admin user
        self.register("admin", "AdminPass123!", "admin@enterprise.io", role="admin")

    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def register(self, username: str, password: str, email: str, role: str = "user") -> Tuple[bool, str]:
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters"
        if username in self.users:
            return False, "Username already exists"
        
        salt = hashlib.md5(username.encode()).hexdigest()
        hashed = self._hash_password(password, salt)
        self.users[username] = {
            "username": username,
            "password_hash": hashed,
            "salt": salt,
            "email": email,
            "role": role,
            "is_active": True
        }
        return True, "User registered successfully"

    def login(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        user = self.users.get(username)
        if not user or not user["is_active"]:
            return False, None
        expected_hash = self._hash_password(password, user["salt"])
        if user["password_hash"] == expected_hash:
            token = self.token_manager.generate_token(username)
            return True, token
        return False, None

    def authorize(self, token: str, required_role: str = "user") -> bool:
        username = self.token_manager.get_user_for_token(token)
        if not username:
            return False
        user = self.users.get(username)
        if not user:
            return False
        if required_role == "admin" and user["role"] != "admin":
            return False
        return True
