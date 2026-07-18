from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from beanie.operators import RegEx, In

from backend.core.security import get_current_user
from backend.models.user import UserProfile
from backend.models.job import JobPosting, JobStatus
from backend.schemas.common import PaginatedResponse, APIResponse
from backend.schemas.job import JobFilters, JobResponse

router = APIRouter()

@router.get("", response_model=APIResponse[PaginatedResponse[JobResponse]])
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    location: Optional[str] = None,
    current_user: UserProfile = Depends(get_current_user)
):
    """List jobs with pagination and filters"""
    query = {}
    
    if status:
        query["status"] = status
    if min_score is not None:
        query["score"] = {"$gte": min_score}
    if source:
        query["source_name"] = source
    if search:
        query["title"] = {"$regex": f".*{search}.*", "$options": "i"}
    if location:
        query["location"] = {"$regex": f".*{location}.*", "$options": "i"}

    # Execute query
    total = await JobPosting.find(query).count()
    
    # Sort by score desc, then created_at desc
    jobs = await JobPosting.find(query).sort([("score", -1), ("created_at", -1)]).skip((page - 1) * page_size).limit(page_size).to_list()
    
    return APIResponse(
        success=True,
        data=PaginatedResponse(
            items=[JobResponse.model_validate(j.model_dump(by_alias=True, mode="json")) for j in jobs],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
    )

@router.get("/{id}", response_model=APIResponse[JobResponse])
async def get_job(id: str, current_user: UserProfile = Depends(get_current_user)):
    """Get a single job by ID"""
    job = await JobPosting.get(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return APIResponse(success=True, data=JobResponse.model_validate(job.model_dump(by_alias=True, mode="json")))

@router.post("/crawl", response_model=APIResponse[str])
async def trigger_crawl(current_user: UserProfile = Depends(get_current_user)):
    """Manually trigger a crawl task"""
    # Only allow if we have celery configured. For now we will invoke the task asynchronously.
    try:
        from backend.workers.crawlers import crawl_all_sources
        crawl_all_sources.delay()
        return APIResponse(success=True, message="Crawl task started in the background")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/score", response_model=APIResponse[str])
async def trigger_score(current_user: UserProfile = Depends(get_current_user)):
    """Manually trigger the scoring task"""
    try:
        from backend.workers.scorer import score_new_jobs
        score_new_jobs.delay()
        return APIResponse(success=True, message="Scoring task started in the background")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
