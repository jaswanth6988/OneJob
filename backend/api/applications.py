import os
import logging
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from beanie import PydanticObjectId

from backend.core.security import get_current_user
from backend.models.user import UserProfile
from backend.models.job import JobPosting, JobStatus
from backend.models.resume import Resume
from backend.models.application import JobApplication, ApplicationStatus
from backend.schemas.common import APIResponse
from backend.schemas.application import ApplicationResponse, ApplicationStartRequest

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=APIResponse[List[ApplicationResponse]])
async def list_applications(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    current_user: UserProfile = Depends(get_current_user)
):
    """List all job applications for the authenticated user."""
    filters = [JobApplication.user_id.id == current_user.id]
    if status:
        filters.append(JobApplication.status == status)
        
    apps = await JobApplication.find(*filters).sort([("updated_at", -1)]).limit(limit).to_list()
    
    # Clean serialization for ObjectId fields to prevent Pydantic 500 errors
    items = []
    for app in apps:
        data = app.model_dump(by_alias=True, mode="json")
        data["_id"] = str(app.id)
        data["user_id"] = str(app.user_id.ref.id if hasattr(app.user_id, "ref") else app.user_id)
        data["job_id"] = str(app.job_id.ref.id if hasattr(app.job_id, "ref") else app.job_id)
        if app.resume_id:
            data["resume_id"] = str(app.resume_id.ref.id if hasattr(app.resume_id, "ref") else app.resume_id)
        items.append(ApplicationResponse.model_validate(data))

    return APIResponse(success=True, data=items)

@router.post("/start/{job_id}", response_model=APIResponse[ApplicationResponse])
async def start_job_application(
    job_id: str,
    request_data: Optional[ApplicationStartRequest] = None,
    current_user: UserProfile = Depends(get_current_user)
):
    """Start an automated job application for a specific job posting."""
    job = await JobPosting.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found.")

    mode = request_data.mode if request_data and request_data.mode else "DRY_RUN"
    
    # Resolve best resume
    resume = None
    if request_data and request_data.resume_id:
        resume = await Resume.get(request_data.resume_id)
    if not resume:
        resume = await Resume.find(
            Resume.user_id.id == current_user.id, 
            Resume.is_active == True
        ).sort([("created_at", -1)]).first_or_none()

    # Create new Application tracker record
    application = JobApplication(
        user_id=current_user,
        job_id=job,
        resume_id=resume,
        status=ApplicationStatus.QUEUED,
        mode=mode,
        apply_url=job.apply_url or job.url or ""
    )
    await application.insert()
    
    # Update job status
    job.status = JobStatus.APPLYING
    await job.save()

    # Trigger Celery background worker
    try:
        from backend.workers.auto_applier import apply_to_job
        apply_to_job.delay(str(application.id))
        logger.info(f"Queued background auto_apply task for Application {application.id}")
    except Exception as e:
        logger.warning(f"Celery queue error: {e}. Worker might need manual trigger or fallback.")

    data = application.model_dump(by_alias=True, mode="json")
    data["_id"] = str(application.id)
    data["user_id"] = str(current_user.id)
    data["job_id"] = str(job.id)
    if resume:
        data["resume_id"] = str(resume.id)
        
    return APIResponse(success=True, message="Automated job application started successfully.", data=ApplicationResponse.model_validate(data))

@router.get("/{app_id}", response_model=APIResponse[ApplicationResponse])
async def get_application_details(app_id: str, current_user: UserProfile = Depends(get_current_user)):
    """Retrieve execution logs, AI answers, and screenshots for a specific application."""
    app = await JobApplication.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application record not found.")
        
    data = app.model_dump(by_alias=True, mode="json")
    data["_id"] = str(app.id)
    data["user_id"] = str(app.user_id.ref.id if hasattr(app.user_id, "ref") else app.user_id)
    data["job_id"] = str(app.job_id.ref.id if hasattr(app.job_id, "ref") else app.job_id)
    if app.resume_id:
        data["resume_id"] = str(app.resume_id.ref.id if hasattr(app.resume_id, "ref") else app.resume_id)

    return APIResponse(success=True, data=ApplicationResponse.model_validate(data))
