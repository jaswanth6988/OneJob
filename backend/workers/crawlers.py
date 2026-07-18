import logging
from backend.core.celery_app import celery_app, run_async
from backend.core.database import init_db, close_db
from backend.connectors.remoteok import RemoteOKConnector
from backend.connectors.adzuna import AdzunaConnector
from backend.services.job_manager import job_manager

logger = logging.getLogger(__name__)

async def _async_crawl_all_sources():
    await init_db()
    
    total_new_jobs = 0
    connectors = [
        RemoteOKConnector(),
        AdzunaConnector()
    ]
    
    # We can pass user preferences from DB here if we wanted to customize the crawl,
    # but for now we'll do a generic crawl for standard keywords to build the DB.
    default_keywords = ["Software Engineer", "Frontend", "Backend", "Full Stack", "Data"]
    
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
    """
    Periodic task to crawl all configured job sources.
    """
    logger.info("Crawl All Sources task started")
    result = run_async(_async_crawl_all_sources())
    
    # Trigger scoring for any NEW jobs
    from backend.workers.scorer import score_new_jobs
    score_new_jobs.delay()
    
    return f"Crawled {result} new jobs"
