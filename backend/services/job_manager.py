import logging
from typing import List, Optional
from datetime import datetime, timezone
import re

from backend.models.job import JobPosting, JobStatus
from backend.connectors.base import BaseJobConnector

logger = logging.getLogger(__name__)

class JobManagerService:
    """
    Handles normalization, deduplication, and saving of jobs fetched from connectors.
    """
    def __init__(self):
        pass

    def generate_duplicate_key(self, company: str, title: str) -> str:
        """
        Generates a unique key to prevent saving the same job multiple times.
        Strips special characters and lowercases.
        """
        def slugify(text: str) -> str:
            text = text.lower()
            text = re.sub(r'[^a-z0-9\s]', '', text)
            return "-".join(text.split())
            
        company_slug = slugify(company)
        title_slug = slugify(title)
        
        return f"{company_slug}:{title_slug}"

    async def save_jobs_from_connector(self, connector: BaseJobConnector, keywords: List[str] = None, location: str = None) -> int:
        """
        Fetches jobs from a connector, normalizes them, deduplicates, and saves them to DB.
        Returns the number of NEW jobs saved.
        """
        new_jobs_count = 0
        
        try:
            async for raw_job in connector.fetch_jobs(keywords=keywords, location=location):
                # 1. Normalize
                job: JobPosting = connector.normalize_job(raw_job)
                
                # 2. Deduplicate
                dup_key = self.generate_duplicate_key(job.company, job.title)
                job.duplicate_key = dup_key
                
                # Check if it exists in DB
                existing_job = await JobPosting.find_one(JobPosting.duplicate_key == dup_key)
                
                if existing_job:
                    # Update discovered_at or any other fields if needed, but don't overwrite status/score
                    existing_job.updated_at = datetime.now(timezone.utc)
                    await existing_job.save()
                else:
                    # Save new job
                    await job.insert()
                    new_jobs_count += 1
                    
        except Exception as e:
            logger.error(f"Error in save_jobs_from_connector for {connector.source_name}: {e}")
            
        return new_jobs_count

job_manager = JobManagerService()
