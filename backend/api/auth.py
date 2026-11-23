from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.models.user import UserProfile
from backend.schemas.user import UserCreate, TokenResponse, UserProfileResponse
from backend.schemas.common import APIResponse
from backend.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, get_current_user

router = APIRouter()

@router.post("/register", response_model=APIResponse[UserProfileResponse])
async def register(user_in: UserCreate):
    user = await UserProfile.find_one(UserProfile.email == user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    hashed_password = get_password_hash(user_in.password)
    user = UserProfile(
        email=user_in.email,
        hashed_password=hashed_password,
        name=user_in.name
    )
    await user.insert()
    
    return APIResponse(
        success=True,
        message="User registered successfully",
        data=UserProfileResponse.model_validate(user.model_dump(by_alias=True, mode="json"))
    )

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserProfile.find_one(UserProfile.email == form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id)
    )

from pydantic import BaseModel
from jose import jwt, JWTError
from backend.core.config import settings

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest):
    try:
        payload = jwt.decode(body.refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise ValueError("Wrong token type")
        user = await UserProfile.get(payload.get("sub"))
        if not user or not user.is_active:
            raise ValueError("Inactive account")
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=create_refresh_token(user.id))

@router.get("/me", response_model=APIResponse[UserProfileResponse])
async def get_me(current_user: UserProfile = Depends(get_current_user)):
    return APIResponse(
        success=True,
        data=UserProfileResponse.model_validate(current_user.model_dump(by_alias=True, mode="json"))
    )
