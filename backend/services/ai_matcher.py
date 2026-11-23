import json
from backend.core.llm import generate_content
import logging
from typing import List
from datetime import datetime, timezone

from backend.core.config import settings
from backend.models.job import JobPosting, JobStatus
from backend.models.resume import Resume

logger = logging.getLogger(__name__)



class AIMatcherService:
    """
    Scores job postings against candidate resumes using Gemini REST API.
    Uses pure async HTTP — no gRPC SDK, fully Windows Defender compliant.
    """

    async def score_job(self, job: JobPosting, resumes: List[Resume]) -> JobPosting:
        if not resumes:
            logger.warning(f"No resumes provided to score job {job.id}")
            return job

        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY missing. Skipping AI scoring.")
            return job

        # Build resume context
        resume_context = ""
        for r in resumes:
            resume_context += f"--- Resume: {r.title} ---\n"
            resume_context += f"Skills: {', '.join(r.skills)}\n"
            if r.experience:
                resume_context += "Experience:\n"
                for exp in r.experience[:3]:
                    resume_context += f"  - {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})\n"
            resume_context += "\n"

        prompt = f"""You are an expert ATS (Applicant Tracking System) AI assistant.
Evaluate how well the candidate's resume matches the job description.

JOB:
Title: {job.title}
Company: {job.company}
Description: {job.description[:1500]}

CANDIDATE RESUME:
{resume_context}

Return ONLY a strict JSON object:
{{
  "score": integer (0 to 100),
  "matched_skills": [list of strings — skills candidate has that match the job],
  "missing_skills": [list of strings — critical skills required but missing from resume],
  "confidence_reasoning": string (1-2 sentence explanation of the score)
}}"""

        try:
            result_data = await generate_content(prompt, json_response=True, max_retries=3)
            
            if not result_data:
                logger.warning(f"Failed to score job {job.id} (likely rate limited). Will retry next cycle.")
                return job # Stays NEW

            score = max(0, min(100, float(result_data.get("score", 0))))
            matched = result_data.get("matched_skills", [])
            missing = result_data.get("missing_skills", [])
            reason = result_data.get("confidence_reasoning", "")

            job.score = score
            job.match_result = {
                "matched_skills": matched,
                "missing_skills": missing,
                "reason": reason,
                "confidence": 0.0,
            }

            # Update status based on score thresholds
            if score >= settings.SCORE_MATCHED:
                job.status = JobStatus.MATCHED
            elif score >= settings.SCORE_PARTIAL:
                job.status = JobStatus.PARTIAL_MATCHED
            else:
                job.status = JobStatus.SKIPPED

            logger.info(f"Scored '{job.title}' → {score}/100 ({job.status})")
            return job

        except Exception as e:
            logger.error(f"Unexpected error scoring job {job.id}: {e}")
            return job  # Stay NEW — retry next cycle


ai_matcher = AIMatcherService()
