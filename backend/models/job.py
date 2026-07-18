from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import Field
from beanie import Document, Indexed

class JobStatus(str, Enum):
    NEW = "NEW"
    MATCHED = "MATCHED"
    PARTIAL_MATCHED = "PARTIAL_MATCHED"
    APPLYING = "APPLYING"
    APPLIED = "APPLIED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"

class RemoteType(str, Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"
    UNKNOWN = "UNKNOWN"

class JobPosting(Document):
    source_name: str
    source_job_id: str
    title: str
    company: str
    location: Optional[str] = None
    remote_type: RemoteType = RemoteType.UNKNOWN
    
    description: str
    url: str
    salary_range: Optional[str] = None
    apply_url: Optional[str] = None
    
    skills_required: List[str] = Field(default_factory=list)
    seniority_level: Optional[str] = None
    industry: Optional[str] = None
    
    normalized_fields: Dict[str, Any] = Field(default_factory=dict)
    
    score: float = 0.0
    status: JobStatus = JobStatus.NEW
    match_result: Dict[str, Any] = Field(default_factory=dict)
    
    duplicate_key: Indexed(str)
    tags: List[str] = Field(default_factory=list)
    is_priority_company: bool = False
    
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "jobs"
