from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.security import get_current_user
from backend.models.user import UserProfile
from backend.schemas.common import APIResponse

router = APIRouter()


class PreferencesUpdate(BaseModel):
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    expected_salary: Optional[str] = None
    notice_period: Optional[str] = None
    work_authorization: Optional[str] = None
    priority_companies: Optional[List[str]] = None
    github_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    portfolio_links: Optional[List[str]] = None


@router.get("", response_model=APIResponse[dict])
async def get_preferences(current_user: UserProfile = Depends(get_current_user)):
    """Get the current user's job search preferences."""
    return APIResponse(
        success=True,
        data={
            "preferred_roles": current_user.preferred_roles,
            "preferred_locations": current_user.preferred_locations,
            "expected_salary": current_user.expected_salary,
            "notice_period": current_user.notice_period,
            "work_authorization": current_user.work_authorization,
            "priority_companies": current_user.priority_companies,
            "github_link": current_user.github_link,
            "linkedin_link": current_user.linkedin_link,
            "portfolio_links": current_user.portfolio_links,
            "name": current_user.name,
            "phone": current_user.phone,
            "location": current_user.location,
            "email": current_user.email,
        }
    )


@router.put("", response_model=APIResponse[dict])
async def update_preferences(
    data: PreferencesUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update the current user's job search preferences."""
    update_fields = data.model_dump(exclude_unset=True)
    update_fields["updated_at"] = datetime.now(timezone.utc)

    if update_fields:
        await current_user.set(update_fields)

    return APIResponse(success=True, message="Preferences saved successfully.", data=update_fields)
