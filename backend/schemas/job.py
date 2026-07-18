from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from backend.models.job import JobStatus, RemoteType

class JobFilters(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    remote_type: Optional[RemoteType] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    status: Optional[JobStatus] = None
    source: Optional[str] = None
    skills: Optional[List[str]] = None
    seniority: Optional[str] = None
    is_priority: Optional[bool] = None
    sort_by: Optional[str] = "created_at"
    page: int = 1
    page_size: int = 20

class JobMatchResult(BaseModel):
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    reason: str = ""
    recommended_resume_id: Optional[str] = None

class JobResponse(BaseModel):
    id: str = Field(alias="_id")
    source_name: str
    source_job_id: str
    title: str
    company: str
    location: Optional[str]
    remote_type: RemoteType
    description: str
    url: str
    salary_range: Optional[str]
    apply_url: Optional[str]
    skills_required: List[str]
    seniority_level: Optional[str]
    industry: Optional[str]
    score: float
    status: JobStatus
    match_result: Dict[str, Any]
    tags: List[str]
    is_priority_company: bool
    discovered_at: datetime
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class JobListResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    company: str
    location: Optional[str]
    remote_type: RemoteType
    score: float
    status: JobStatus
    created_at: datetime

    class Config:
        populate_by_name = True
