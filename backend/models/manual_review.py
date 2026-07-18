from typing import List, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import Field
from beanie import Document, Link
from backend.models.application import ApplicationAttempt
from backend.models.job import JobPosting

class ManualReviewReason(str, Enum):
    CAPTCHA_DETECTED = "CAPTCHA_DETECTED"
    IP_BLOCKED = "IP_BLOCKED"
    LAYOUT_CHANGED = "LAYOUT_CHANGED"
    FIELD_MISMATCH = "FIELD_MISMATCH"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    LOGIN_EXPIRED = "LOGIN_EXPIRED"
    MFA_REQUIRED = "MFA_REQUIRED"
    ANSWER_NOT_RECOGNIZED = "ANSWER_NOT_RECOGNIZED"
    FILE_INVALID = "FILE_INVALID"
    UNKNOWN_EXCEPTION = "UNKNOWN_EXCEPTION"
    PAGE_TIMEOUT = "PAGE_TIMEOUT"

class ReviewSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ManualReviewItem(Document):
    attempt_id: Link[ApplicationAttempt]
    job_id: Link[JobPosting]
    
    reason: ManualReviewReason
    severity: ReviewSeverity
    
    failed_step: str
    recommended_action: Optional[str] = None
    evidence_links: List[str] = Field(default_factory=list)
    ai_summary: Optional[str] = None
    user_notes: Optional[str] = None
    
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "manual_reviews"
