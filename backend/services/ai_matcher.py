import json
import logging
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from backend.core.config import settings
from backend.models.job import JobPosting, JobStatus
from backend.models.resume import Resume
from backend.models.ai_event import AIEventLog

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class AIMatchOutput(BaseModel):
    score: int = Field(description="Match score from 0 to 100")
    matched_skills: List[str] = Field(description="List of skills that perfectly match the job requirements")
    missing_skills: List[str] = Field(description="List of critical skills required by the job that are missing from the resume")
    confidence_reasoning: str = Field(description="Brief explanation (1-2 sentences) of why this score was given")
    recommended_resume_id: Optional[str] = Field(description="The ID of the best matching resume if multiple were provided, otherwise the ID of the single resume", default=None)


class AIMatcherService:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={"response_mime_type": "application/json"}
        )

    async def score_job(self, job: JobPosting, resumes: List[Resume]) -> JobPosting:
        """
        Scores a job against a list of resumes using Gemini.
        Updates the job's score, status, and match_result in place.
        """
        if not resumes:
            logger.warning(f"No resumes provided to score job {job.id}")
            return job

        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is missing. Skipping AI scoring.")
            return job

        resume_context = ""
        for r in resumes:
            resume_context += f"--- Resume ID: {r.id} | Title: {r.title} ---\n"
            resume_context += f"Skills: {', '.join(r.skills)}\n"
            resume_context += "Experience:\n"
            for exp in r.experience:
                resume_context += f" - {exp.get('title')} at {exp.get('company')} ({exp.get('duration')})\n"
                for bullet in exp.get('bullets', []):
                    resume_context += f"   * {bullet}\n"
            resume_context += "\n"

        prompt = f"""
        You are an expert ATS (Applicant Tracking System) AI assistant.
        Your task is to evaluate how well the candidate's resume(s) match the given job description.

        JOB DETAILS:
        Title: {job.title}
        Company: {job.company}
        Description:
        {job.description}

        CANDIDATE RESUMES:
        {resume_context}

        Evaluate the match and return a strict JSON object matching this schema:
        {{
            "score": integer (0 to 100),
            "matched_skills": [string],
            "missing_skills": [string],
            "confidence_reasoning": string,
            "recommended_resume_id": string (the ID of the resume that best matches)
        }}
        """

        try:
            # We use synchronous generate_content because the async version is not always stable
            # in the genai SDK, but we wrap it in a try-except
            response = self.model.generate_content(prompt)
            
            # The response is guaranteed to be JSON due to response_mime_type config
            result_data = json.loads(response.text)
            
            # Validate with Pydantic
            validated = AIMatchOutput(**result_data)
            
            # Update the job
            job.score = float(validated.score)
            job.match_result = {
                "matched_skills": validated.matched_skills,
                "missing_skills": validated.missing_skills,
                "confidence": 0.95, # High confidence if structured parsing succeeded
                "reason": validated.confidence_reasoning,
                "recommended_resume_id": validated.recommended_resume_id
            }
            
            # Update status based on thresholds
            if job.score >= settings.SCORE_AUTO_APPLY:
                # If we want to auto-apply later, we might set it to APPLYING
                job.status = JobStatus.MATCHED
            elif job.score >= settings.SCORE_MATCHED:
                job.status = JobStatus.MATCHED
            elif job.score >= settings.SCORE_PARTIAL:
                job.status = JobStatus.PARTIAL_MATCHED
            else:
                job.status = JobStatus.SKIPPED
                
            return job
            
        except Exception as e:
            logger.error(f"Error scoring job {job.id} with Gemini: {str(e)}")
            job.status = JobStatus.FAILED
            job.match_result = {"error": str(e)}
            return job

# Singleton instance
ai_matcher = AIMatcherService()
