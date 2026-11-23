import logging
from backend.core.llm import generate_content
from typing import Optional

from backend.core.config import settings
from backend.models.job import JobPosting
from backend.models.resume import Resume

logger = logging.getLogger(__name__)

class AIScreeningResponder:
    async def generate_answer(self, question_text: str, job: JobPosting, resume: Optional[Resume] = None) -> str:
        """
        Uses Gemini REST API (via httpx) to dynamically generate a tailored answer to an application form question.
        Using direct HTTP REST prevents C++ gRPC/cygrpc DLL locking issues on Windows environments while keeping execution 100% async.
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("AI provider unavailable; screening answers require manual review")
        resume_info = "No candidate evidence available. Do not invent facts."
        if resume:
            resume_info = f"Title: {resume.title}\nSkills: {', '.join(resume.skills)}\nText Summary: {resume.parsed_text[:1500]}"

        prompt = f"""
        You are acting as the job applicant applying for a role. You are filling out an online job application form.
        Generate a professional, accurate, and concise response to the following application question based on the candidate's background and the job description.

        JOB DETAILS:
        Title: {job.title}
        Company: {job.company}
        Description Excerpt: {job.description[:1000]}

        CANDIDATE BACKGROUND:
        {resume_info}

        QUESTION FROM APPLICATION FORM:
        "{question_text}"

        RULES:
        1. Answer directly and concisely as the candidate (in first person 'I').
        2. Never invent years, qualifications, authorization, achievements, or other facts. Return NEEDS_REVIEW when evidence is missing.
        3. Return NEEDS_REVIEW for salary, legal declarations, consent, work authorization, or sensitive information not explicitly provided.
        4. Keep conversational answers under 3 sentences unless requested otherwise.
        5. Return ONLY the final plaintext response string to be entered directly into the form input box, without introductory filler or markdown formatting.
        """

        answer = await generate_content(prompt, max_retries=2, timeout=15.0)
        
        if answer and "NEEDS_REVIEW" not in answer:
            logger.info("Generated evidence-based screening draft")
            return answer

        raise ValueError("Screening answer needs review; insufficient evidence or provider failure")

ai_responder = AIScreeningResponder()
