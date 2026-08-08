from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import Field
from beanie import Document, Indexed, Link

from backend.models.user import UserProfile
from backend.models.job import JobPosting
from backend.models.resume import Resume

class ApplicationStatus(str, Enum):
    QUEUED = "QUEUED"
    APPLYING = "APPLYING"
    SUBMITTED = "SUBMITTED"
    REQUIRES_MANUAL_INTERVENTION = "REQUIRES_MANUAL_INTERVENTION"
    FAILED = "FAILED"

class JobApplication(Document):
    user_id: Link[UserProfile]
    job_id: Link[JobPosting]
    resume_id: Optional[Link[Resume]] = None
    
    status: ApplicationStatus = ApplicationStatus.QUEUED
    mode: str = "DRY_RUN"  # Options: DRY_RUN, LIVE
    apply_url: str = ""
    
    submitted_fields: Dict[str, Any] = Field(default_factory=dict)
    ai_answers: List[Dict[str, str]] = Field(default_factory=list)
    screenshots: List[str] = Field(default_factory=list)
    error_log: Optional[str] = None
    
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "job_applications"
