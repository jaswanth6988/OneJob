import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.security import get_current_user
from backend.models.user import UserProfile
from backend.models.job import JobPosting
from backend.models.resume import Resume
from backend.schemas.common import APIResponse
from backend.services.interview_coach import interview_coach

router = APIRouter()
logger = logging.getLogger(__name__)


class EvaluateAnswerRequest(BaseModel):
    job_id: str
    question: str
    answer: str
    resume_id: Optional[str] = None


@router.post("/questions/{job_id}", response_model=APIResponse[List[dict]])
async def generate_interview_questions(
    job_id: str,
    resume_id: Optional[str] = None,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Generates a tailored set of 9 interview questions (3 behavioral,
    3 technical, 3 culture-fit) for a specific job.
    """
    job = await JobPosting.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    resume = None
    if resume_id:
        resume = await Resume.get(resume_id)
        if not resume or str(resume.user_id.ref.id if hasattr(resume.user_id, "ref") else resume.user_id.id) != str(current_user.id):
            raise HTTPException(status_code=404, detail="Resume not found")
    if not resume:
        resume = await Resume.find(
            {"user_id": current_user.to_ref()},
            Resume.is_active == True
        ).sort([("created_at", -1)]).first_or_none()

    try:
        questions = await interview_coach.generate_questions(job, resume)
        return APIResponse(success=True, data=questions)
    except Exception as e:
        logger.error(f"Interview question generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate", response_model=APIResponse[dict])
async def evaluate_interview_answer(
    request: EvaluateAnswerRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Evaluates a candidate's answer to an interview question.
    Returns score, verdict, strengths, improvements, and a model ideal answer.
    """
    job = await JobPosting.get(request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    resume = None
    if request.resume_id:
        resume = await Resume.get(request.resume_id)
        if not resume or str(resume.user_id.ref.id if hasattr(resume.user_id, "ref") else resume.user_id.id) != str(current_user.id):
            raise HTTPException(status_code=404, detail="Resume not found")
    if not resume:
        resume = await Resume.find(
            {"user_id": current_user.to_ref()},
            Resume.is_active == True
        ).sort([("created_at", -1)]).first_or_none()

    try:
        evaluation = await interview_coach.evaluate_answer(request.question, request.answer, job, resume)
        return APIResponse(success=True, data=evaluation)
    except Exception as e:
        logger.error(f"Answer evaluation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
