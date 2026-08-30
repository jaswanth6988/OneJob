from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from beanie.operators import RegEx, In

from backend.core.security import get_current_user
from backend.models.user import UserProfile
from backend.models.job import JobPosting, JobStatus
from backend.schemas.common import PaginatedResponse, APIResponse
from backend.schemas.job import JobFilters, JobResponse
from pydantic import BaseModel

class CrawlRequest(BaseModel):
    search: Optional[str] = None

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
    remote_type: Optional[str] = None,
    sort_by: Optional[str] = Query("score", description="Sort by 'score' or 'latest'"),
    current_user: UserProfile = Depends(get_current_user)
):
    """List jobs with pagination and filters"""
    filters = []
    
    if status:
        filters.append(JobPosting.status == status)
    if min_score is not None:
        filters.append(JobPosting.score >= min_score)
    if source:
        filters.append(JobPosting.source_name == source)
    if search:
        from beanie.operators import Or
        filters.append(
            Or(
                RegEx(JobPosting.title, f".*{search}.*", "i"),
                RegEx(JobPosting.company, f".*{search}.*", "i")
            )
        )
    if location:
        filters.append(RegEx(JobPosting.location, f".*{location}.*", "i"))
    if remote_type:
        filters.append(JobPosting.remote_type == remote_type)

    # Execute query
    find_query = JobPosting.find(*filters) if filters else JobPosting.find_all()
    total = await find_query.count()
    
    # Sort
    sort_opts = [("score", -1), ("created_at", -1)]
    if sort_by == "latest":
        sort_opts = [("created_at", -1)]
        
    jobs = await find_query.sort(sort_opts).skip((page - 1) * page_size).limit(page_size).to_list()
    
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

@router.post("/crawl", response_model=APIResponse[str])
async def trigger_crawl(req: Optional[CrawlRequest] = None, current_user: UserProfile = Depends(get_current_user)):
    """Manually trigger a crawl task"""
    try:
        from backend.workers.crawlers import crawl_all_sources
        search_str = req.search if req else None
        crawl_all_sources.delay(search_str)
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

@router.get("/{id}", response_model=APIResponse[JobResponse])
async def get_job(id: str, current_user: UserProfile = Depends(get_current_user)):
    """Get a single job by ID"""
    job = await JobPosting.get(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return APIResponse(success=True, data=JobResponse.model_validate(job.model_dump(by_alias=True, mode="json")))

@router.post("/{id}/score", response_model=APIResponse[JobResponse])
async def score_single_job(id: str, current_user: UserProfile = Depends(get_current_user)):
    """Synchronously score a single job"""
    job = await JobPosting.get(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    from backend.models.resume import Resume
    from backend.services.ai_matcher import ai_matcher
    
    active_resumes = await Resume.find(Resume.is_active == True).to_list()
    if not active_resumes:
        raise HTTPException(status_code=400, detail="No active resumes found. Upload and activate a resume first.")
        
    try:
        updated_job = await ai_matcher.score_job(job, active_resumes)
        await updated_job.save()
        return APIResponse(success=True, data=JobResponse.model_validate(updated_job.model_dump(by_alias=True, mode="json")))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

