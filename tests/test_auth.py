import pytest
from app.authentication.auth_service import AuthService
from app.authentication.tokens import TokenManager

@pytest.fixture
def auth_service():
    token_mgr = TokenManager(secret_key="test-key", token_ttl=300)
    return AuthService(token_manager=token_mgr)

def test_login_admin_success(auth_service):
    ok, token = auth_service.login("admin", "AdminPass123!")
    assert ok is True
    assert token is not None

def test_login_admin_invalid_password(auth_service):
    ok, token = auth_service.login("admin", "WrongPassword")
    assert ok is False
    assert token is None

def test_register_new_user(auth_service):
    ok, msg = auth_service.register("johndoe", "Secret123!", "john@example.com")
    assert ok is True
    assert "successfully" in msg

def test_register_duplicate_user(auth_service):
    auth_service.register("unique_user", "Secret123!", "u@example.com")
    ok, msg = auth_service.register("unique_user", "Other123!", "u2@example.com")
    assert ok is False
    assert "already exists" in msg

def test_authorization_role(auth_service):
    _, token = auth_service.login("admin", "AdminPass123!")
    assert auth_service.authorize(token, required_role="admin") is True
    
    auth_service.register("regular_user", "UserPass123!", "user@example.com", role="user")
    _, user_token = auth_service.login("regular_user", "UserPass123!")
    assert auth_service.authorize(user_token, required_role="admin") is False
    assert auth_service.authorize(user_token, required_role="user") is True

def test_token_expiration():
    token_mgr = TokenManager(secret_key="key", token_ttl=-1)
    token = token_mgr.generate_token("expired_user")
    assert token_mgr.validate_token(token) is False
