from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from backend.models.application import ApplicationStatus

class ApplicationStartRequest(BaseModel):
    mode: Optional[str] = "DRY_RUN"  # Options: DRY_RUN, LIVE
    resume_id: Optional[str] = None  # If omitted, picks best matching active resume

class ApplicationResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: Optional[Any] = None
    job_id: Optional[Any] = None
    resume_id: Optional[Any] = None
    
    status: ApplicationStatus
    mode: str
    apply_url: str
    
    submitted_fields: Dict[str, Any] = Field(default_factory=dict)
    ai_answers: List[Dict[str, str]] = Field(default_factory=list)
    screenshots: List[str] = Field(default_factory=list)
    error_log: Optional[str] = None
    
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        extra = "ignore"
