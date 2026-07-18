from typing import List, Optional
from datetime import datetime, timezone
from pydantic import EmailStr, Field
from beanie import Document, Indexed

class UserProfile(Document):
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    expected_salary: Optional[str] = None
    notice_period: Optional[str] = None
    work_authorization: Optional[str] = None
    
    portfolio_links: List[str] = Field(default_factory=list)
    github_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    
    priority_companies: List[str] = Field(default_factory=list)
    priority_roles: List[str] = Field(default_factory=list)
    
    is_active: bool = True
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
