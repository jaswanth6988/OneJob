import httpx
import logging
from typing import AsyncGenerator, Dict, List, Optional
import re
from backend.models.job import JobPosting, RemoteType, JobStatus
from backend.connectors.base import BaseJobConnector

logger = logging.getLogger(__name__)

class JobicyConnector(BaseJobConnector):
    @property
    def source_name(self) -> str:
        return "Jobicy"

    async def fetch_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        remote_only: bool = False,
        limit: int = 50,
    ) -> AsyncGenerator[Dict, None]:
        url = "https://jobicy.com/api/v2/remote-jobs"
        params = {"count": limit}
        if keywords and len(keywords) > 0:
            params["tag"] = keywords[0]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                jobs = data.get("jobs", [])
                
                for job in jobs:
                    yield job
            except Exception as e:
                logger.error(f"Jobicy fetch error: {e}")

    def normalize_job(self, raw_job: Dict) -> JobPosting:
        import html
        desc = html.unescape(raw_job.get("jobDescription", ""))
        desc = re.sub(r'<[^>]+>', '', desc)
        
        return JobPosting(
            source_name=self.source_name,
            source_job_id=str(raw_job.get("id")),
            title=raw_job.get("jobTitle", "Unknown Title"),
            company=raw_job.get("companyName", "Unknown Company"),
            location=raw_job.get("jobGeo", ""),
            remote_type=RemoteType.REMOTE,
            description=desc[:5000],
            url=raw_job.get("url", ""),
            apply_url=raw_job.get("url", ""),
            skills_required=[],
            tags=[],
            score=0.0,
            status=JobStatus.NEW,
            is_priority_company=False
        )
