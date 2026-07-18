from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from backend.models.application import ApplicationStatus
from backend.schemas.job import JobListResponse

class ApplicationResponse(BaseModel):
    id: str = Field(alias="_id")
    job_id: Any  # Can be expanded
    resume_id: Any
    user_id: Any
    status: ApplicationStatus
    failure_reason: Optional[str]
    failure_step: Optional[str]
    retry_count: int
    max_retries: int
    screenshot_paths: List[str]
    logs_path: Optional[str]
    submitted_payload_summary: Dict[str, Any]
    applied_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class ApplicationListResponse(BaseModel):
    id: str = Field(alias="_id")
    job_id: Any
    status: ApplicationStatus
    applied_at: Optional[datetime]
    created_at: datetime

    class Config:
        populate_by_name = True
