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
            logger.warning("GEMINI_API_KEY missing. Returning default candidate response.")
            return "I am excited about this opportunity and confident my skills align well with the team's needs. Please refer to my attached resume for comprehensive details."

        resume_info = "Candidate is an experienced software engineer and full stack developer."
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
        2. If asked for years of experience or numbers, estimate reasonably based on skills or state a reasonable figure (e.g. "3+ years").
        3. If asked for salary expectations, respond politely like "Negotiable based on total compensation package and market standards."
        4. Keep conversational answers under 3 sentences unless requested otherwise.
        5. Return ONLY the final plaintext response string to be entered directly into the form input box, without introductory filler or markdown formatting.
        """

        answer = await generate_content(prompt, max_retries=2, timeout=15.0)
        
        if answer:
            logger.info(f"Generated AI response for question '{question_text}': {answer}")
            return answer

        return "I have a strong technical background and immense enthusiasm for this domain, and look forward to discussing how my experience can contribute to your goals."

ai_responder = AIScreeningResponder()
