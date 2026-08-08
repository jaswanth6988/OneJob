import httpx
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.security import get_current_user
from backend.core.config import settings
from backend.models.user import UserProfile
from backend.models.resume import Resume
from backend.schemas.common import APIResponse

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

SYSTEM_CONTEXT = (
    "You are an expert AI career coach embedded inside an AI-powered Job Application Portal. "
    "You help candidates with resume writing, interview preparation, job search strategy, salary negotiation, "
    "career transitions, and cover letter drafting. Be encouraging, specific, and actionable. "
    "Keep responses concise (under 200 words) unless asked for detail. "
    "Use clear structure when listing multiple points."
)


@router.post("", response_model=APIResponse[dict])
async def chat(
    request: ChatRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="AI unavailable: GEMINI_API_KEY not configured.")

    resume_context = ""
    try:
        resume = await Resume.find(Resume.is_active == True).sort([("created_at", -1)]).first_or_none()
        if resume:
            skills_str = ", ".join(resume.skills[:15]) if resume.skills else "Not specified"
            resume_context = f"\n\nCANDIDATE CONTEXT:\nResume: {resume.title}\nSkills: {skills_str}"
    except Exception:
        pass

    history_text = ""
    if request.history:
        for msg in request.history[-6:]:
            label = "User" if msg.role == "user" else "Assistant"
            history_text += f"\n{label}: {msg.content}"

    prompt = (
        f"{SYSTEM_CONTEXT}{resume_context}\n\n"
        f"CONVERSATION:{history_text if history_text else ' (new conversation)'}\n\n"
        f"User: {request.message}\nAssistant:"
    )

    url = GEMINI_URL.format(
        model=settings.GEMINI_MODEL or "gemini-2.0-flash",
        key=settings.GEMINI_API_KEY
    )

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
            if resp.status_code == 200:
                reply = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                return APIResponse(success=True, data={"reply": reply})
            logger.warning(f"Gemini chat API {resp.status_code}: {resp.text[:200]}")
            return APIResponse(
                success=True,
                data={"reply": "I'm having trouble reaching the AI service right now. Please try again shortly."}
            )
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return APIResponse(
            success=True,
            data={"reply": "I'm temporarily unavailable. Please check your connection and try again."}
        )
