from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from backend.models.resume import RoleLabel

class ResumeParsedData(BaseModel):
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    certifications: List[str]
    raw_text: str

class ResumeCreate(BaseModel):
    title: str
    version_name: str
    role_label: RoleLabel

class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    version_name: Optional[str] = None
    role_label: Optional[RoleLabel] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[str]] = None
    parsed_text: Optional[str] = None

class ResumeResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    version_name: str
    role_label: RoleLabel
    file_path: str
    original_filename: str
    file_type: str
    parsed_text: str
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    certifications: List[str]
    ats_score: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class ResumeListResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    version_name: str
    role_label: RoleLabel
    ats_score: float
    created_at: datetime

    class Config:
        populate_by_name = True
