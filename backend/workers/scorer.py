import logging
from backend.core.celery_app import celery_app, run_async
from backend.core.database import init_db, close_db
from backend.models.job import JobPosting, JobStatus
from backend.models.resume import Resume
from backend.services.ai_matcher import ai_matcher

logger = logging.getLogger(__name__)

async def _async_score_new_jobs(user_id: str = None):
    await init_db()
    
    from backend.models.user import UserProfile
    user = await UserProfile.get(user_id) if user_id else None
    if not user:
        await close_db()
        return 0
    # 1. Get the requesting account's active resumes
    active_resumes = await Resume.find(Resume.is_active == True, {"user_id": user.to_ref()}).to_list()
    if not active_resumes:
        logger.warning("No active resumes found. Skipping scoring.")
        await close_db()
        return 0

    # 2. Get all NEW jobs (limit to 50 at a time to prevent timeout)
    new_jobs = await JobPosting.find({f"user_matches.{user_id}": {"$exists": False}}).limit(50).to_list()
    
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
            await JobPosting.find_one(JobPosting.id == job.id).update({"$set": {f"user_matches.{user_id}": {"score": updated_job.score, "match_result": updated_job.match_result, "status": updated_job.status}}})
            scored_count += 1
            
            # Be polite to the API, but rely on backend.core.llm's exponential backoff for actual rate limits
            import asyncio
            await asyncio.sleep(1.0) 
            
        except Exception as e:
            logger.error(f"Error saving scored job {job.id}: {e}")
            
    await close_db()
    return scored_count

@celery_app.task(name="backend.workers.scorer.score_new_jobs")
def score_new_jobs(user_id: str = None):
    """
    Task to score any newly discovered jobs against the user's active resumes.
    """
    logger.info("Scorer task started")
    result = run_async(_async_score_new_jobs(user_id))
    return f"Scored {result} jobs"
