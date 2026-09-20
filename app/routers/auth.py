from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.authentication.auth_service import AuthService
from app.authentication.tokens import TokenManager

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

auth_service = AuthService()

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    role: Optional[str] = "user"

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str

class UserProfileResponse(BaseModel):
    username: str
    email: str
    role: str
    is_active: bool

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(req: RegisterRequest):
    success, message = auth_service.register(
        username=req.username,
        password=req.password,
        email=req.email,
        role=req.role or "user"
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"message": message, "username": req.username}

@router.post("/login", response_model=TokenResponse)
def login_user(req: LoginRequest):
    success, token = auth_service.login(req.username, req.password)
    if not success or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    user = auth_service.users[req.username]
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        username=req.username,
        role=user["role"]
    )

@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(token: str):
    username = auth_service.token_manager.get_user_for_token(token)
    if not username or username not in auth_service.users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = auth_service.users[username]
    return UserProfileResponse(
        username=user["username"],
        email=user["email"],
        role=user["role"],
        is_active=user["is_active"]
    )
