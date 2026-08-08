import logging
from typing import Optional
from backend.core.celery_app import celery_app, run_async
from backend.core.database import init_db, close_db
from backend.models.application import JobApplication, ApplicationStatus
from backend.models.job import JobPosting
from backend.models.resume import Resume
from backend.models.user import UserProfile
from backend.automation.engine import automation_engine

logger = logging.getLogger(__name__)

async def _async_apply_to_job(application_id: str):
    await init_db()
    
    application = await JobApplication.get(application_id, fetch_links=True)
    if not application:
        logger.error(f"Application ID {application_id} not found in DB.")
        await close_db()
        return "Application not found"

    # In Beanie with fetch_links=True, link fields are populated with actual Document instances if found
    job = application.job_id
    user = application.user_id
    resume = application.resume_id

    # Fallback if links were not auto-populated as documents
    if isinstance(job, object) and not isinstance(job, JobPosting) and hasattr(job, "ref"):
        job = await JobPosting.get(job.ref.id)
    elif not isinstance(job, JobPosting):
        job = await JobPosting.get(str(application.job_id))
        
    if not isinstance(user, UserProfile):
        user = await UserProfile.find_one() # For single tenant/demo fallback

    if application.resume_id and not isinstance(resume, Resume):
        resume = await Resume.get(str(application.resume_id))
    elif not resume:
        # Pick highest scoring or latest active resume
        resume = await Resume.find(Resume.is_active == True).sort([("created_at", -1)]).first_or_none()

    if not job or not user:
        logger.error("Missing job or user profile for application execution.")
        application.status = ApplicationStatus.FAILED
        application.error_log = "Failed to resolve job or user profile from DB."
        await application.save()
        await close_db()
        return "Failed resolution"

    logger.info(f"Executing auto-apply for Job '{job.title}' (App ID: {application_id})")
    await automation_engine.execute_application(application, job, user, resume)
    
    await close_db()
    return f"Completed application {application_id} with status {application.status}"

@celery_app.task(name="backend.workers.auto_applier.apply_to_job", bind=True, max_retries=1)
def apply_to_job(self, application_id: str):
    """
    Celery task to run browser automation for a single JobApplication.
    """
    logger.info(f"Received apply_to_job task for ID: {application_id}")
    try:
        result = run_async(_async_apply_to_job(application_id))
        return result
    except Exception as exc:
        logger.error(f"Task apply_to_job failed: {exc}", exc_info=True)
        self.retry(exc=exc, countdown=10)
