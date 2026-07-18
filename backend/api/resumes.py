import os
import aiofiles
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from backend.models.user import UserProfile
from backend.models.resume import Resume, RoleLabel
from backend.schemas.resume import ResumeResponse, ResumeListResponse, ResumeUpdate
from backend.schemas.common import APIResponse
from backend.core.security import get_current_user
from backend.core.config import settings
from backend.core.logging import get_logger
from backend.services.resume_parser import parse_resume

router = APIRouter()
logger = get_logger(__name__)

@router.post("/upload", response_model=APIResponse[ResumeResponse])
async def upload_resume(
    title: str = Form(...),
    version_name: str = Form(...),
    role_label: RoleLabel = Form(RoleLabel.GENERAL),
    file: UploadFile = File(...),
    current_user: UserProfile = Depends(get_current_user)
):
    # Validate file type
    filename = file.filename
    ext = filename.split(".")[-1].lower() if filename else ""
    if ext not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")

    # Create storage directory
    os.makedirs(settings.STORAGE_RESUMES, exist_ok=True)
    
    # Save file
    file_id = f"{current_user.id}_{datetime.now().timestamp()}_{filename}"
    file_path = os.path.join(settings.STORAGE_RESUMES, file_id)
    
    try:
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
            
        # Parse resume
        parsed_data = parse_resume(file_path, ext)
        
        # Create DB record
        resume = Resume(
            user_id=current_user,
            title=title,
            version_name=version_name,
            role_label=role_label,
            file_path=file_path,
            original_filename=filename,
            file_type=ext,
            parsed_text=parsed_data.raw_text,
            skills=parsed_data.skills,
            experience=parsed_data.experience,
            education=parsed_data.education,
            certifications=parsed_data.certifications
        )
        await resume.insert()
        
        return APIResponse(
            success=True,
            message="Resume uploaded and parsed successfully",
            data=ResumeResponse.model_validate(resume.model_dump(by_alias=True))
        )
    except Exception as e:
        logger.error("Failed to process resume upload", exc_info=True)
        # Cleanup file if it was created
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")

@router.get("", response_model=APIResponse[List[ResumeListResponse]])
async def list_resumes(current_user: UserProfile = Depends(get_current_user)):
    resumes = await Resume.find(Resume.user_id.id == current_user.id, Resume.is_active == True).to_list()
    return APIResponse(
        success=True,
        data=[ResumeListResponse.model_validate(r.model_dump(by_alias=True)) for r in resumes]
    )

@router.get("/{id}", response_model=APIResponse[ResumeResponse])
async def get_resume(id: str, current_user: UserProfile = Depends(get_current_user)):
    resume = await Resume.get(id)
    if not resume or resume.user_id.id != current_user.id or not resume.is_active:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    return APIResponse(
        success=True,
        data=ResumeResponse.model_validate(resume.model_dump(by_alias=True))
    )

@router.put("/{id}", response_model=APIResponse[ResumeResponse])
async def update_resume(
    id: str,
    update_data: ResumeUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    resume = await Resume.get(id)
    if not resume or resume.user_id.id != current_user.id or not resume.is_active:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    data = update_data.model_dump(exclude_unset=True)
    if data:
        data["updated_at"] = datetime.now(timezone.utc)
        await resume.set(data)
        
    return APIResponse(
        success=True,
        message="Resume updated successfully",
        data=ResumeResponse.model_validate(resume.model_dump(by_alias=True))
    )

@router.delete("/{id}", response_model=APIResponse)
async def delete_resume(id: str, current_user: UserProfile = Depends(get_current_user)):
    resume = await Resume.get(id)
    if not resume or resume.user_id.id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Soft delete
    await resume.set({"is_active": False, "updated_at": datetime.now(timezone.utc)})
    
    return APIResponse(
        success=True,
        message="Resume deleted successfully"
    )
