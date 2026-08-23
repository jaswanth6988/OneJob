import logging
from backend.core.celery_app import celery_app, run_async
from backend.core.database import init_db, close_db
from backend.connectors.remoteok import RemoteOKConnector
from backend.connectors.adzuna import AdzunaConnector
from backend.connectors.remotive import RemotiveConnector
from backend.connectors.jobicy import JobicyConnector
from backend.connectors.arbeitnow import ArbeitnowConnector
from backend.connectors.rss import RssConnector
from backend.models.job import RemoteType
from backend.services.job_manager import job_manager

logger = logging.getLogger(__name__)


async def _async_crawl_all_sources():
    await init_db()

    total_new_jobs = 0
    connectors = [
        RemoteOKConnector(),
        RemotiveConnector(),
        AdzunaConnector(),
        JobicyConnector(),
        ArbeitnowConnector(),
        RssConnector("WeWorkRemotely", "https://weworkremotely.com/categories/remote-programming-jobs.rss"),
        RssConnector("Python.org", "https://www.python.org/jobs/feed/rss/", RemoteType.UNKNOWN),
        RssConnector("Remote.co", "https://remote.co/remote-jobs/feed/"),
        RssConnector("Relocate.me", "https://relocate.me/rss", RemoteType.UNKNOWN),
        RssConnector("DevITjobs", "https://devitjobs.com/rss"),
    ]

    # Pull keywords from user preferences + active resume skills so crawl is personalized
    from backend.models.resume import Resume
    from backend.models.user import UserProfile

    default_keywords = [
        "Python", "React", "Next.js", "FastAPI", "JavaScript", "TypeScript",
        "Full Stack", "Backend", "Frontend", "Software Engineer", "AI",
        "Node.js", "REST API", "MongoDB", "DevOps", "Cloud", "Machine Learning"
    ]

    try:
        # Layer 1: Resume skills
        active_resume = await Resume.find(Resume.is_active == True).sort([("created_at", -1)]).first_or_none()
        if active_resume and active_resume.skills:
            default_keywords = list(dict.fromkeys(active_resume.skills[:10] + default_keywords))[:20]

        # Layer 2: User preferred roles (highest priority)
        user = await UserProfile.find_one()
        if user and user.preferred_roles:
            default_keywords = list(dict.fromkeys(user.preferred_roles + default_keywords))[:20]

        logger.info(f"Crawling with personalized keywords: {default_keywords[:6]}...")
    except Exception as e:
        logger.warning(f"Could not load personalized keywords: {e}")

    for connector in connectors:
        logger.info(f"Starting crawl for {connector.source_name}")
        try:
            count = await job_manager.save_jobs_from_connector(
                connector=connector,
                keywords=default_keywords,
            )
            logger.info(f"Saved {count} new jobs from {connector.source_name}")
            total_new_jobs += count
        except Exception as e:
            logger.error(f"Failed crawling {connector.source_name}: {e}")

    await close_db()
    return total_new_jobs


@celery_app.task(name="backend.workers.crawlers.crawl_all_sources")
def crawl_all_sources():
    """Periodic task to crawl all configured job sources."""
    logger.info("Crawl All Sources task started")
    result = run_async(_async_crawl_all_sources())

    from backend.workers.scorer import score_new_jobs
    score_new_jobs.delay()

    return f"Crawled {result} new jobs"
