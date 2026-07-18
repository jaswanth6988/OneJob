from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import Field
from beanie import Document, Link
from backend.models.user import UserProfile

class RoleLabel(str, Enum):
    GENERAL = "General"
    DEVELOPER = "Developer"
    DATA_AI = "Data_AI"
    CLOUD = "Cloud"
    SECURITY = "Security"
    CUSTOM = "Custom"

class Resume(Document):
    user_id: Link[UserProfile]
    title: str
    version_name: str
    role_label: RoleLabel = RoleLabel.GENERAL
    
    file_path: str
    original_filename: str
    file_type: str  # "pdf" or "docx"
    
    parsed_text: str = ""
    skills: List[str] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    
    ats_score: float = 0.0
    is_active: bool = True
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "resumes"
