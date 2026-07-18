from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import Field
from beanie import Document, Link
from backend.models.user import UserProfile
from backend.models.resume import Resume
from backend.models.job import JobPosting

class ApplicationStatus(str, Enum):
    PENDING = "PENDING"
    APPLYING = "APPLYING"
    APPLIED = "APPLIED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    RETRYING = "RETRYING"

class ApplicationAttempt(Document):
    job_id: Link[JobPosting]
    resume_id: Link[Resume]
    user_id: Link[UserProfile]
    
    status: ApplicationStatus = ApplicationStatus.PENDING
    failure_reason: Optional[str] = None
    failure_step: Optional[str] = None
    
    retry_count: int = 0
    max_retries: int = 2
    
    screenshot_paths: List[str] = Field(default_factory=list)
    logs_path: Optional[str] = None
    submitted_payload_summary: Dict[str, Any] = Field(default_factory=dict)
    
    applied_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "application_attempts"
