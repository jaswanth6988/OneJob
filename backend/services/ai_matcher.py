import json
import httpx
import logging
from typing import List
from datetime import datetime, timezone

from backend.core.config import settings
from backend.models.job import JobPosting, JobStatus
from backend.models.resume import Resume

logger = logging.getLogger(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"


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

        url = GEMINI_URL.format(
            model=settings.GEMINI_MODEL or "gemini-2.0-flash",
            key=settings.GEMINI_API_KEY
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(url, json=payload)

            if resp.status_code == 429:
                # Quota exhausted — leave job as NEW so it retries next time
                logger.warning(f"Gemini quota exceeded scoring job {job.id}. Will retry next cycle.")
                return job  # Status stays NEW

            if resp.status_code != 200:
                logger.error(f"Gemini HTTP {resp.status_code} scoring job {job.id}: {resp.text[:200]}")
                return job  # Status stays NEW on any API error

            raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            result_data = json.loads(raw_text)

            score = float(result_data.get("score", 0))
            matched = result_data.get("matched_skills", [])
            missing = result_data.get("missing_skills", [])
            reason = result_data.get("confidence_reasoning", "")

            job.score = score
            job.match_result = {
                "matched_skills": matched,
                "missing_skills": missing,
                "reason": reason,
                "confidence": 0.95,
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

        except json.JSONDecodeError as je:
            logger.error(f"Failed to parse Gemini JSON for job {job.id}: {je}")
            return job  # Stay NEW — don't mark FAILED on parse error
        except Exception as e:
            logger.error(f"Unexpected error scoring job {job.id}: {e}")
            return job  # Stay NEW — retry next cycle


ai_matcher = AIMatcherService()
