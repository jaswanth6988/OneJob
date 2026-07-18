import asyncio
from celery import Celery
from backend.core.config import settings

# Create Celery app
celery_app = Celery(
    "ai_job_portal",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["backend.workers.crawlers", "backend.workers.scorer"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Worker concurrency and limits
    worker_concurrency=2,
    worker_prefetch_multiplier=1,
)

# Optional: Periodic task scheduling (Celery Beat)
celery_app.conf.beat_schedule = {
    'crawl-jobs-every-hour': {
        'task': 'backend.workers.crawlers.crawl_all_sources',
        'schedule': settings.CRAWL_INTERVAL_MINUTES * 60.0,
    },
}

def run_async(coro):
    """
    Helper to run async functions synchronously in celery tasks.
    Creates a new event loop for the thread.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
