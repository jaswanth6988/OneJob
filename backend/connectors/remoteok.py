import httpx
import logging
from typing import AsyncGenerator, Dict, List, Optional
from datetime import datetime, timezone
import json

from backend.connectors.base import BaseJobConnector
from backend.models.job import JobPosting, RemoteType, JobStatus

logger = logging.getLogger(__name__)

class RemoteOKConnector(BaseJobConnector):
    """
    Connector for RemoteOK (remoteok.com/api)
    """
    
    @property
    def source_name(self) -> str:
        return "RemoteOK"
        
    async def fetch_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        remote_only: bool = True,  # RemoteOK is always remote
        limit: int = 50,
    ) -> AsyncGenerator[Dict, None]:
        url = "https://remoteok.com/api"
        # RemoteOK API has limited filtering, so we fetch and filter locally
        # Though it supports 'tags' param: ?tags=react,node
        
        params = {}
        if keywords:
            params['tags'] = ",".join([k.lower().replace(" ", "-") for k in keywords[:2]])
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # RemoteOK API returns an array where the first element is legal info
                # Skip the first element if it's not a job
                jobs = [j for j in data if j.get("id") and j.get("company")]
                
                for i, job in enumerate(jobs):
                    if i >= limit:
                        break
                    yield job
            except Exception as e:
                logger.error(f"Error fetching from {self.source_name}: {e}")

    def normalize_job(self, raw_job: Dict) -> JobPosting:
        # RemoteOK uses tags, we map them to skills
        tags = raw_job.get("tags", [])
        
        description = raw_job.get("description", "")
        
        # RemoteOK locations are often 'Worldwide' or specific regions
        location = raw_job.get("location", "")
        
        return JobPosting(
            source_name=self.source_name,
            source_job_id=str(raw_job.get("id")),
            title=raw_job.get("position", "Unknown Position"),
            company=raw_job.get("company", "Unknown Company"),
            location=location if location else None,
            remote_type=RemoteType.REMOTE,
            description=description,
            url=raw_job.get("url", ""),
            salary_range=f"${raw_job.get('salary_min', 0)} - ${raw_job.get('salary_max', 0)}" if raw_job.get('salary_min') or raw_job.get('salary_max') else None,
            apply_url=raw_job.get("apply_url", raw_job.get("url", "")),
            skills_required=tags,
            status=JobStatus.NEW,
            tags=tags,
            discovered_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
