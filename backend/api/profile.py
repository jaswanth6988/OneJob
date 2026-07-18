from fastapi import APIRouter, Depends
from backend.models.user import UserProfile
from backend.schemas.user import UserProfileUpdate, UserProfileResponse
from backend.schemas.common import APIResponse
from backend.core.security import get_current_user
from datetime import datetime, timezone

router = APIRouter()

@router.get("", response_model=APIResponse[UserProfileResponse])
async def get_profile(current_user: UserProfile = Depends(get_current_user)):
    return APIResponse(
        success=True,
        data=UserProfileResponse.model_validate(current_user.model_dump(by_alias=True))
    )

@router.put("", response_model=APIResponse[UserProfileResponse])
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    update_data = profile_update.model_dump(exclude_unset=True)
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc)
        await current_user.set(update_data)
        
    return APIResponse(
        success=True,
        message="Profile updated successfully",
        data=UserProfileResponse.model_validate(current_user.model_dump(by_alias=True))
    )
