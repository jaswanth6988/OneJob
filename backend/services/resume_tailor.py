from backend.core.llm import generate_content
import logging
from typing import Optional, Dict, Any

from backend.core.config import settings
from backend.models.job import JobPosting
from backend.models.resume import Resume

logger = logging.getLogger(__name__)




class ResumeTailorService:
    """
    Analyzes a resume against a specific job posting and returns
    tailored improvement recommendations and an ATS score.
    """

    async def tailor(self, resume: Resume, job: JobPosting) -> Dict[str, Any]:
        """
        Returns a structured tailoring analysis dict with:
        - tailored_ats_score (int 0–100)
        - summary_rewrite (str)
        - skills_to_add (list[str])
        - skills_to_highlight (list[str])
        - bullet_improvements (list[dict])
        - keyword_gaps (list[str])
        - overall_advice (str)
        """
        resume_text = resume.parsed_text[:3000] if resume.parsed_text else ""
        skills_str = ", ".join(resume.skills) if resume.skills else "Not specified"

        prompt = f"""
You are an expert ATS resume consultant and career coach. Analyze the candidate's resume against the job description and return a JSON object.

JOB DETAILS:
Title: {job.title}
Company: {job.company}
Description:
{job.description[:2000]}

CANDIDATE RESUME:
Title: {resume.title}
Current Skills: {skills_str}
Resume Text:
{resume_text}

Return a strict JSON object with EXACTLY these fields:
{{
  "tailored_ats_score": integer (0 to 100, how well the resume matches this specific job after tailoring),
  "current_ats_score": integer (0 to 100, how well the resume matches AS-IS without changes),
  "summary_rewrite": string (a rewritten professional summary/objective paragraph of 2-3 sentences, tailored for this specific job),
  "skills_to_add": array of strings (important skills from the job description completely missing from the resume — max 8),
  "skills_to_highlight": array of strings (skills candidate already has that are highly relevant and should be moved to the top — max 8),
  "keyword_gaps": array of strings (important ATS keywords in the job description not present in the resume — max 10),
  "bullet_improvements": array of objects with fields "original" (string) and "improved" (string) — suggest improved versions of up to 3 experience bullet points to better match the job,
  "overall_advice": string (2-3 sentences of strategic advice for this application)
}}
        """

        try:
            result = await generate_content(prompt, json_response=True, max_retries=2)
            if not result:
                return self._fallback_response(resume, job)

            # Validate required keys exist
            required = ["tailored_ats_score", "summary_rewrite", "skills_to_add", "keyword_gaps", "overall_advice"]
            for key in required:
                if key not in result:
                    raise ValueError(f"Missing key: {key}")
            return result
        except Exception as e:
            logger.error(f"Failed to parse tailor response: {e}")
            return self._fallback_response(resume, job)

    def _fallback_response(self, resume: Resume, job: JobPosting) -> Dict[str, Any]:
        return {
            "tailored_ats_score": 65,
            "current_ats_score": 50,
            "summary_rewrite": f"Results-driven professional with proven experience seeking the {job.title} role at {job.company}. Passionate about delivering high-impact solutions aligned with the team's mission.",
            "skills_to_add": ["Communication", "Problem Solving", "Collaboration"],
            "skills_to_highlight": resume.skills[:5],
            "keyword_gaps": [],
            "bullet_improvements": [],
            "overall_advice": "Focus on quantifying your achievements and aligning your language with the job description's key phrases. Customize your summary for every application."
        }


resume_tailor = ResumeTailorService()
