from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    expected_salary: Optional[str] = None
    notice_period: Optional[str] = None
    work_authorization: Optional[str] = None
    portfolio_links: Optional[List[str]] = None
    github_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    priority_companies: Optional[List[str]] = None
    priority_roles: Optional[List[str]] = None

class UserProfileResponse(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    name: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    preferred_roles: List[str]
    preferred_locations: List[str]
    expected_salary: Optional[str]
    notice_period: Optional[str]
    work_authorization: Optional[str]
    portfolio_links: List[str]
    github_link: Optional[str]
    linkedin_link: Optional[str]
    priority_companies: List[str]
    priority_roles: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
