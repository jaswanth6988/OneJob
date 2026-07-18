import httpx
import logging
import os
from typing import AsyncGenerator, Dict, List, Optional
from datetime import datetime, timezone

from backend.connectors.base import BaseJobConnector
from backend.models.job import JobPosting, RemoteType, JobStatus

logger = logging.getLogger(__name__)

class AdzunaConnector(BaseJobConnector):
    """
    Connector for Adzuna API
    Requires ADZUNA_APP_ID and ADZUNA_APP_KEY in env or config
    """
    
    def __init__(self, app_id: str = None, app_key: str = None, country: str = "us"):
        self.app_id = app_id or os.environ.get("ADZUNA_APP_ID")
        self.app_key = app_key or os.environ.get("ADZUNA_APP_KEY")
        self.country = country
        
    @property
    def source_name(self) -> str:
        return "Adzuna"
        
    async def fetch_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        remote_only: bool = False,
        limit: int = 50,
    ) -> AsyncGenerator[Dict, None]:
        if not self.app_id or not self.app_key:
            logger.warning("Adzuna credentials missing, skipping fetch.")
            return

        # Adzuna uses a paginated URL structure: /jobs/{country}/search/{page}
        url = f"https://api.adzuna.com/v1/api/jobs/{self.country}/search/1"
        
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": min(limit, 50),
        }
        
        if keywords:
            params["what"] = " ".join(keywords)
        if location:
            params["where"] = location
        # If remote_only is requested, we can try to append 'remote' to keywords
        if remote_only:
            params["what"] = params.get("what", "") + " remote"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                for job in results:
                    yield job
                    
            except Exception as e:
                logger.error(f"Error fetching from {self.source_name}: {e}")

    def normalize_job(self, raw_job: Dict) -> JobPosting:
        title = raw_job.get("title", "Unknown Title")
        
        # Determine remote status based on title/location heuristic
        location_dict = raw_job.get("location", {})
        location_str = ", ".join(location_dict.get("area", []))
        
        remote_type = RemoteType.UNKNOWN
        if "remote" in title.lower() or "remote" in location_str.lower():
            remote_type = RemoteType.REMOTE
        
        salary_min = raw_job.get("salary_min")
        salary_max = raw_job.get("salary_max")
        salary_range = None
        if salary_min or salary_max:
            salary_range = f"${int(salary_min) if salary_min else 0} - ${int(salary_max) if salary_max else '?'}"
            
        return JobPosting(
            source_name=self.source_name,
            source_job_id=str(raw_job.get("id")),
            title=title,
            company=raw_job.get("company", {}).get("display_name", "Unknown Company"),
            location=location_str if location_str else None,
            remote_type=remote_type,
            description=raw_job.get("description", ""),
            url=raw_job.get("redirect_url", ""),
            salary_range=salary_range,
            apply_url=raw_job.get("redirect_url", ""),
            skills_required=[],  # Adzuna doesn't provide structured skills well
            status=JobStatus.NEW,
            tags=[],
            discovered_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
