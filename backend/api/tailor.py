import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.security import get_current_user
from backend.models.user import UserProfile
from backend.models.job import JobPosting
from backend.models.resume import Resume
from backend.schemas.common import APIResponse
from backend.services.resume_tailor import resume_tailor

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{job_id}", response_model=APIResponse[dict])
async def tailor_resume_for_job(
    job_id: str,
    resume_id: Optional[str] = None,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Generates a tailored resume analysis for a specific job posting
    using the user's active resume (or a specified resume_id).
    """
    job = await JobPosting.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found.")

    resume = None
    if resume_id:
        resume = await Resume.get(resume_id)
    if not resume:
        resume = await Resume.find(
            Resume.user_id.id == current_user.id,
            Resume.is_active == True
        ).sort([("created_at", -1)]).first_or_none()

    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found. Please upload a resume first.")

    try:
        analysis = await resume_tailor.tailor(resume, job)
        return APIResponse(
            success=True,
            message="Resume tailoring analysis complete.",
            data=analysis
        )
    except Exception as e:
        logger.error(f"Resume tailor error for job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Tailoring failed: {str(e)}")
