import asyncio
import uuid
import socket
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from beanie.operators import RegEx, In

from backend.core.security import get_current_user
from backend.models.user import UserProfile
from backend.models.job import JobPosting, JobStatus
from backend.schemas.common import PaginatedResponse, APIResponse
from backend.schemas.job import JobFilters, JobResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

_local_crawl_tasks: dict[str, str] = {}

async def _run_local_crawl(task_id: str, search_query: Optional[str], user_id: str):
    _local_crawl_tasks[task_id] = "PENDING"
    try:
        from backend.workers.crawlers import _async_crawl_all_sources
        await _async_crawl_all_sources(search_query=search_query, user_id=user_id, close_db_on_finish=False)
        _local_crawl_tasks[task_id] = "SUCCESS"
        logger.info(f"Local crawl completed successfully for task {task_id}")
    except Exception as e:
        logger.error(f"Local crawl failed for task {task_id}: {e}")
        _local_crawl_tasks[task_id] = "FAILURE"

class CrawlRequest(BaseModel):
    search: Optional[str] = None

router = APIRouter()

def personalized_job(job, user):
    data = job.model_dump(by_alias=True, mode="json")
    match = job.user_matches.get(str(user.id), {})
    data.update(score=match.get("score", 0), match_result=match.get("match_result", {}), status=match.get("status", "NEW"))
    return JobResponse.model_validate(data)


@router.get("", response_model=APIResponse[PaginatedResponse[JobResponse]])
async def list_jobs(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=200),
    location: Optional[str] = Query(None, max_length=200),
    company: Optional[str] = Query(None, max_length=200),
    remote_type: Optional[str] = None, source: Optional[str] = None,
    seniority: Optional[str] = None, industry: Optional[str] = None,
    skills: Optional[str] = Query(None, max_length=300),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    status: Optional[str] = None,
    posted_days: Optional[int] = Query(None, ge=1, le=365),
    salary_only: bool = False, include_expired: bool = False, saved: bool = False,
    sort_by: str = Query("latest", pattern="^(latest|oldest|score|company)$"),
    current_user: UserProfile = Depends(get_current_user)
):
    from backend.services.job_filters import build_job_filters
    from beanie import PydanticObjectId
    arguments = dict(locals())
    arguments.update(min_score=None, status=None)
    query = build_job_filters(**arguments)
    personal = f"user_matches.{current_user.id}"
    if min_score is not None:
        query = {"$and": [query, {f"{personal}.score": {"$gte": min_score}}]}
    if status:
        query = {"$and": [query, {f"{personal}.status": status}]}
    if saved:
        query = {"$and": [query, {"_id": {"$in": [PydanticObjectId(i) for i in current_user.saved_jobs]}}]}
    find_query = JobPosting.find(query)
    total = await find_query.count()
    sorts = {"latest": [("discovered_at", -1)], "oldest": [("discovered_at", 1)], "score": [(f"{personal}.score", -1)], "company": [("company", 1)]}
    jobs = await find_query.sort(sorts[sort_by] + [("_id", 1)]).skip((page - 1) * page_size).limit(page_size).to_list()
    return APIResponse(success=True, data=PaginatedResponse(
        items=[personalized_job(j, current_user) for j in jobs],
        total=total, page=page, page_size=page_size, pages=(total + page_size - 1) // page_size))

@router.get("/facets", response_model=APIResponse[dict])
async def job_facets(current_user: UserProfile = Depends(get_current_user)):
    collection = JobPosting.get_motor_collection()
    return APIResponse(success=True, data={
        "sources": sorted(x for x in await collection.distinct("source_name") if x),
        "seniority": sorted(x for x in await collection.distinct("seniority_level") if x),
        "industries": sorted(x for x in await collection.distinct("industry") if x),
        "saved_jobs": current_user.saved_jobs,
    })

@router.put("/{id}/save", response_model=APIResponse[dict])
async def save_job(id: str, current_user: UserProfile = Depends(get_current_user)):
    from beanie import PydanticObjectId
    if not PydanticObjectId.is_valid(id) or not await JobPosting.get(id):
        raise HTTPException(status_code=404, detail="Job not found")
    await current_user.update({"$addToSet": {"saved_jobs": id}})
    return APIResponse(success=True, data={"saved": True})

@router.delete("/{id}/save", response_model=APIResponse[dict])
async def unsave_job(id: str, current_user: UserProfile = Depends(get_current_user)):
    await current_user.update({"$pull": {"saved_jobs": id}})
    return APIResponse(success=True, data={"saved": False})

@router.post("/crawl", response_model=APIResponse[str])
async def trigger_crawl(req: Optional[CrawlRequest] = None, current_user: UserProfile = Depends(get_current_user)):
    """Trigger a crawl task via Celery if available, or in-process background task if Redis is offline"""
    search_str = req.search if req else None
    user_id_str = str(current_user.id)

    # Try Celery if Redis broker is reachable
    try:
        s = socket.socket()
        s.settimeout(0.5)
        s.connect(("localhost", 6379))
        s.close()
        from backend.workers.crawlers import crawl_all_sources
        task = crawl_all_sources.delay(search_str, user_id_str)
        return APIResponse(success=True, data=task.id, message="Crawl task started in the background")
    except Exception:
        # Fallback: run crawler directly in-process via asyncio
        task_id = str(uuid.uuid4())
        asyncio.create_task(_run_local_crawl(task_id, search_str, user_id_str))
        return APIResponse(success=True, data=task_id, message="Crawl task started in-process")

@router.get("/crawl/status/{task_id}", response_model=APIResponse[str])
async def get_crawl_status(task_id: str, current_user: UserProfile = Depends(get_current_user)):
    """Check status of a background crawl task"""
    if task_id in _local_crawl_tasks:
        return APIResponse(success=True, data=_local_crawl_tasks[task_id])
    try:
        from backend.core.celery_app import celery_app
        res = celery_app.AsyncResult(task_id)
        return APIResponse(success=True, data=res.status)
    except Exception:
        return APIResponse(success=True, data="PENDING")

@router.post("/score", response_model=APIResponse[str])
async def trigger_score(current_user: UserProfile = Depends(get_current_user)):
    """Manually trigger the scoring task"""
    try:
        s = socket.socket()
        s.settimeout(0.5)
        s.connect(("localhost", 6379))
        s.close()
        from backend.workers.scorer import score_new_jobs
        score_new_jobs.delay(str(current_user.id))
        return APIResponse(success=True, message="Scoring task started in the background")
    except Exception:
        return APIResponse(success=True, message="Scoring queued (Redis offline, skipped)")

@router.get("/{id}", response_model=APIResponse[JobResponse])
async def get_job(id: str, current_user: UserProfile = Depends(get_current_user)):
    """Get a single job by ID"""
    job = await JobPosting.get(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return APIResponse(success=True, data=personalized_job(job, current_user))

@router.post("/{id}/score", response_model=APIResponse[JobResponse])
async def score_single_job(id: str, current_user: UserProfile = Depends(get_current_user)):
    """Synchronously score a single job"""
    job = await JobPosting.get(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    from backend.core.config import settings
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="Configure GEMINI_API_KEY to enable AI matching")
    from backend.models.resume import Resume
    from backend.services.ai_matcher import ai_matcher
    
    active_resumes = await Resume.find(Resume.is_active == True, {"user_id": current_user.to_ref()}).to_list()
    if not active_resumes:
        raise HTTPException(status_code=400, detail="No active resumes found. Upload and activate a resume first.")
        
    try:
        updated_job = await ai_matcher.score_job(job, active_resumes)
        await JobPosting.find_one(JobPosting.id == job.id).update({"$set": {f"user_matches.{current_user.id}": {"score": updated_job.score, "match_result": updated_job.match_result, "status": updated_job.status}}})
        updated_job = await JobPosting.get(id)
        return APIResponse(success=True, data=personalized_job(updated_job, current_user))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

