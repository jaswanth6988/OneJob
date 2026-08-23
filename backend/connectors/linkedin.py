import httpx
import logging
from typing import AsyncGenerator, Dict, List, Optional
from datetime import datetime, timezone
import urllib.parse
from bs4 import BeautifulSoup

from backend.connectors.base import BaseJobConnector
from backend.models.job import JobPosting, RemoteType, JobStatus

logger = logging.getLogger(__name__)

class LinkedInConnector(BaseJobConnector):
    """
    Scrapes LinkedIn's public job search page.
    No auth required. Limited to whatever LinkedIn exposes publicly without a login wall.
    """
    
    @property
    def source_name(self) -> str:
        return "LinkedIn"
        
    async def fetch_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        remote_only: bool = False,
        limit: int = 50,
    ) -> AsyncGenerator[Dict, None]:
        
        # Build query string
        query = " ".join(keywords) if keywords else "software engineer"
        if remote_only:
            query += " remote"
            
        loc = location if location else "India"
        
        url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(query)}&location={urllib.parse.quote(loc)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='base-card')
                
                for i, card in enumerate(job_cards):
                    if i >= limit:
                        break
                        
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location')
                    link_elem = card.find('a', class_='base-card__full-link')
                    
                    if not title_elem or not link_elem:
                        continue
                        
                    title = title_elem.text.strip()
                    company = company_elem.text.strip() if company_elem else "Unknown Company"
                    job_location = location_elem.text.strip() if location_elem else loc
                    link = link_elem.get('href', '').split('?')[0]  # Remove tracking params
                    
                    # Extract Job ID from URL if possible (e.g. ...-1234567890?...)
                    job_id = link.split('-')[-1] if '-' in link else link
                    
                    yield {
                        "id": job_id,
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "url": link,
                        "description": f"View full description on LinkedIn: {link}"
                    }
                    
            except Exception as e:
                logger.error(f"Error scraping LinkedIn: {e}")

    def normalize_job(self, raw_job: Dict) -> JobPosting:
        title = raw_job.get("title", "")
        location_str = raw_job.get("location", "")
        
        remote_type = RemoteType.UNKNOWN
        if "remote" in title.lower() or "remote" in location_str.lower():
            remote_type = RemoteType.REMOTE
        elif "hybrid" in title.lower() or "hybrid" in location_str.lower():
            remote_type = RemoteType.HYBRID
            
        return JobPosting(
            source_name=self.source_name,
            source_job_id=str(raw_job.get("id", "")),
            title=title,
            company=raw_job.get("company", "Unknown"),
            location=location_str,
            remote_type=remote_type,
            description=raw_job.get("description", ""),
            url=raw_job.get("url", ""),
            apply_url=raw_job.get("url", ""),
            skills_required=[],
            status=JobStatus.NEW,
            tags=[],
            discovered_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
