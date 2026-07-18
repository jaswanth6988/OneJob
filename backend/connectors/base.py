from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List, Optional
from backend.models.job import JobPosting, RemoteType

class BaseJobConnector(ABC):
    """
    Base class for all job board connectors.
    Adapters should implement this interface to fetch jobs from various sources.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the job source (e.g., 'RemoteOK', 'Adzuna')"""
        pass

    @abstractmethod
    async def fetch_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        remote_only: bool = False,
        limit: int = 50,
    ) -> AsyncGenerator[Dict, None]:
        """
        Fetch jobs from the source.
        Yields raw job dictionaries that will be normalized later.
        """
        pass

    @abstractmethod
    def normalize_job(self, raw_job: Dict) -> JobPosting:
        """
        Convert a raw job dictionary from the source into our unified JobPosting model.
        """
        pass
