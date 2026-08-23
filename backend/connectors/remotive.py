import httpx
import logging
from typing import AsyncGenerator, Dict, List, Optional
from datetime import datetime, timezone

from backend.connectors.base import BaseJobConnector
from backend.models.job import JobPosting, RemoteType, JobStatus

logger = logging.getLogger(__name__)


class RemotiveConnector(BaseJobConnector):
    """
    Connector for Remotive.com — free remote job board, no API key required.
    API docs: https://remotive.com/api/remote-jobs
    """

    @property
    def source_name(self) -> str:
        return "Remotive"

    async def fetch_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        remote_only: bool = True,
        limit: int = 50,
    ) -> AsyncGenerator[Dict, None]:
        url = "https://remotive.com/api/remote-jobs"

        # Remotive supports a 'search' query param
        search_term = " ".join(keywords[:3]) if keywords else "software engineer"

        params = {"search": search_term, "limit": limit}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                jobs = data.get("jobs", [])
                logger.info(f"Remotive returned {len(jobs)} jobs for search '{search_term}'")

                for i, job in enumerate(jobs):
                    if i >= limit:
                        break
                    yield job

            except Exception as e:
                logger.error(f"Error fetching from Remotive: {e}")

    def normalize_job(self, raw_job: Dict) -> JobPosting:
        tags = raw_job.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]

        salary = None
        sal_min = raw_job.get("salary_min")
        sal_max = raw_job.get("salary_max")
        if sal_min or sal_max:
            salary = f"${sal_min or 0:,} - ${sal_max or 0:,}"
        elif raw_job.get("salary"):
            salary = str(raw_job["salary"])

        return JobPosting(
            source_name=self.source_name,
            source_job_id=str(raw_job.get("id", "")),
            title=raw_job.get("title", "Unknown Position"),
            company=raw_job.get("company_name", "Unknown Company"),
            location=raw_job.get("candidate_required_location") or "Worldwide",
            remote_type=RemoteType.REMOTE,
            description=raw_job.get("description", ""),
            url=raw_job.get("url", ""),
            apply_url=raw_job.get("url", ""),
            salary_range=salary,
            skills_required=tags,
            tags=tags,
            status=JobStatus.NEW,
            discovered_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
