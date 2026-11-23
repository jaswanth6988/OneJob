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
from backend.automation.policy import readiness

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=APIResponse[List[ApplicationResponse]])
async def list_applications(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    current_user: UserProfile = Depends(get_current_user)
):
    """List all job applications for the authenticated user."""
    filters = [{"user_id": current_user.to_ref()}]
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
        if not resume or str(resume.user_id.ref.id if hasattr(resume.user_id, "ref") else resume.user_id.id) != str(current_user.id):
            raise HTTPException(status_code=404, detail="Resume not found")
    if not resume:
        resume = await Resume.find(
            {"user_id": current_user.to_ref()},
            Resume.is_active == True
        ).sort([("created_at", -1)]).first_or_none()

    check = readiness(current_user, resume, job)
    if not check["ready"]:
        raise HTTPException(status_code=422, detail="; ".join(check["issues"]))
    existing = await JobApplication.find_one({"user_id": current_user.to_ref(), "job_id": job.to_ref(), "mode": mode, "status": {"$in": ["QUEUED", "APPLYING", "SUBMITTED", "REQUIRES_MANUAL_INTERVENTION"]}})
    if existing:
        raise HTTPException(status_code=409, detail="An active, submitted, or uncertain attempt already exists. Review it in Applications.")
    # Create new Application tracker record
    application = JobApplication(
        user_id=current_user,
        job_title=job.title,
        company=job.company,
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
        application.status = ApplicationStatus.FAILED
        application.error_log = "Could not reach the application worker. Please retry."
        await application.save()
        job.status = JobStatus.NEW
        await job.save()
        raise HTTPException(status_code=503, detail="Application worker unavailable. Application was not submitted.")

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
    if not app or str(app.user_id.ref.id if hasattr(app.user_id, "ref") else app.user_id.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Application record not found.")

    data = app.model_dump(by_alias=True, mode="json")
    data["_id"] = str(app.id)
    data["user_id"] = str(app.user_id.ref.id if hasattr(app.user_id, "ref") else app.user_id)
    data["job_id"] = str(app.job_id.ref.id if hasattr(app.job_id, "ref") else app.job_id)
    if app.resume_id:
        data["resume_id"] = str(app.resume_id.ref.id if hasattr(app.resume_id, "ref") else app.resume_id)

    return APIResponse(success=True, data=ApplicationResponse.model_validate(data))

@router.get("/{app_id}/screenshots/{index}")
async def application_screenshot(app_id: str, index: int, current_user: UserProfile = Depends(get_current_user)):
    from pathlib import Path
    from fastapi.responses import FileResponse
    from backend.core.config import settings
    if not PydanticObjectId.is_valid(app_id):
        raise HTTPException(status_code=404, detail="Application not found")
    record = await JobApplication.get(app_id)
    if not record or str(record.user_id.ref.id if hasattr(record.user_id, "ref") else record.user_id.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Application not found")
    if index < 0 or index >= len(record.screenshots):
        raise HTTPException(status_code=404, detail="Screenshot not found")
    path = Path(record.screenshots[index]).resolve()
    if not path.is_relative_to(Path(settings.STORAGE_SCREENSHOTS).resolve()) or not path.is_file():
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return FileResponse(path)

@router.get("/preflight/{job_id}")
async def application_preflight(job_id: str, current_user: UserProfile = Depends(get_current_user)):
    if not PydanticObjectId.is_valid(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    job = await JobPosting.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    resume = await Resume.find({"user_id": current_user.to_ref()}, Resume.is_active == True).sort([("created_at", -1)]).first_or_none()
    return APIResponse(success=True, data=readiness(current_user, resume, job))
