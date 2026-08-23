import httpx
import logging
from typing import AsyncGenerator, Dict, List, Optional
from bs4 import BeautifulSoup
import re
from backend.models.job import JobPosting, RemoteType, JobStatus
from backend.connectors.base import BaseJobConnector

logger = logging.getLogger(__name__)

class RssConnector(BaseJobConnector):
    def __init__(self, name: str, feed_url: str, default_remote: RemoteType = RemoteType.REMOTE):
        self._name = name
        self.feed_url = feed_url
        self.default_remote = default_remote

    @property
    def source_name(self) -> str:
        return self._name

    async def fetch_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        remote_only: bool = False,
        limit: int = 50,
    ) -> AsyncGenerator[Dict, None]:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(self.feed_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, "xml")
                items = soup.find_all("item")[:limit]
                for item in items:
                    title = item.find("title").text if item.find("title") else ""
                    link = item.find("link").text if item.find("link") else ""
                    desc = item.find("description").text if item.find("description") else ""
                    guid = item.find("guid").text if item.find("guid") else link
                    pub_date = item.find("pubDate").text if item.find("pubDate") else ""
                    
                    yield {
                        "title": title,
                        "link": link,
                        "description": desc,
                        "guid": guid,
                        "pub_date": pub_date
                    }
            except Exception as e:
                logger.error(f"{self._name} RSS fetch error: {e}")

    def normalize_job(self, raw_job: Dict) -> JobPosting:
        import html
        desc = html.unescape(raw_job.get("description", ""))
        desc = re.sub(r'<[^>]+>', '', desc)
        
        title = raw_job.get("title", "")
        company = "Unknown Company"
        
        # Try to parse company from standard RSS title formats
        if ":" in title:
            parts = title.split(":", 1)
            company = parts[0].strip()
            title = parts[1].strip()
        elif " at " in title:
            parts = title.rsplit(" at ", 1)
            title = parts[0].strip()
            company = parts[1].strip()
            
        return JobPosting(
            source_name=self.source_name,
            source_job_id=raw_job.get("guid", ""),
            title=title,
            company=company,
            location="",
            remote_type=self.default_remote,
            description=desc[:5000],
            url=raw_job.get("link", ""),
            apply_url=raw_job.get("link", ""),
            skills_required=[],
            tags=[],
            score=0.0,
            status=JobStatus.NEW,
            is_priority_company=False
        )
