import httpx
import logging
from typing import AsyncGenerator, Dict, List, Optional
import re
from backend.models.job import JobPosting, RemoteType, JobStatus
from backend.connectors.base import BaseJobConnector

logger = logging.getLogger(__name__)

class ArbeitnowConnector(BaseJobConnector):
    @property
    def source_name(self) -> str:
        return "Arbeitnow"

    async def fetch_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        remote_only: bool = False,
        limit: int = 50,
    ) -> AsyncGenerator[Dict, None]:
        url = "https://www.arbeitnow.com/api/job-board-api"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                jobs = data.get("data", [])[:limit]
                
                for job in jobs:
                    yield job
            except Exception as e:
                logger.error(f"Arbeitnow fetch error: {e}")

    def normalize_job(self, raw_job: Dict) -> JobPosting:
        import html
        desc = html.unescape(raw_job.get("description", ""))
        desc = re.sub(r'<[^>]+>', '', desc)
        
        remote = raw_job.get("remote", False)
        
        return JobPosting(
            source_name=self.source_name,
            source_job_id=raw_job.get("slug", ""),
            title=raw_job.get("title", "Unknown Title"),
            company=raw_job.get("company_name", "Unknown Company"),
            location=raw_job.get("location", ""),
            remote_type=RemoteType.REMOTE if remote else RemoteType.UNKNOWN,
            description=desc[:5000],
            url=raw_job.get("url", ""),
            apply_url=raw_job.get("url", ""),
            skills_required=raw_job.get("tags", []),
            tags=raw_job.get("tags", []),
            score=0.0,
            status=JobStatus.NEW,
            is_priority_company=False
        )
