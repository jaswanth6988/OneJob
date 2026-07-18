import logging
from backend.core.celery_app import celery_app, run_async
from backend.core.database import init_db, close_db
from backend.models.job import JobPosting, JobStatus
from backend.models.resume import Resume
from backend.services.ai_matcher import ai_matcher

logger = logging.getLogger(__name__)

async def _async_score_new_jobs():
    await init_db()
    
    # 1. Get all active resumes
    active_resumes = await Resume.find(Resume.is_active == True).to_list()
    if not active_resumes:
        logger.warning("No active resumes found. Skipping scoring.")
        await close_db()
        return 0

    # 2. Get all NEW jobs (limit to 50 at a time to prevent timeout)
    new_jobs = await JobPosting.find(JobPosting.status == JobStatus.NEW).limit(50).to_list()
    
    if not new_jobs:
        logger.info("No NEW jobs to score.")
        await close_db()
        return 0
        
    scored_count = 0
    for job in new_jobs:
        logger.info(f"Scoring job: {job.title} at {job.company}")
        try:
            # Score it
            updated_job = await ai_matcher.score_job(job, active_resumes)
            # Save it back
            await updated_job.save()
            scored_count += 1
        except Exception as e:
            logger.error(f"Error saving scored job {job.id}: {e}")
            
    await close_db()
    return scored_count

@celery_app.task(name="backend.workers.scorer.score_new_jobs")
def score_new_jobs():
    """
    Task to score any newly discovered jobs against the user's active resumes.
    """
    logger.info("Scorer task started")
    result = run_async(_async_score_new_jobs())
    return f"Scored {result} jobs"
