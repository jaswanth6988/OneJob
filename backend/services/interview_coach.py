from backend.core.llm import generate_content
import logging
from typing import Optional, Dict, Any, List

from backend.core.config import settings
from backend.models.job import JobPosting
from backend.models.resume import Resume

logger = logging.getLogger(__name__)



class InterviewCoachService:
    """
    Generates tailored interview questions for a job and evaluates
    candidate answers with scored AI feedback.
    """

    async def generate_questions(self, job: JobPosting, resume: Optional[Resume] = None) -> List[Dict[str, Any]]:
        """
        Returns a list of interview questions categorized by type:
        behavioral, technical, and culture-fit.
        Each question has: id, type, question, difficulty, focus_area
        """
        skills_str = ", ".join(resume.skills) if resume and resume.skills else "general software engineering"
        resume_summary = resume.parsed_text[:1000] if resume and resume.parsed_text else ""

        prompt = f"""
You are an expert technical recruiter and interview coach preparing a candidate for a job interview.

JOB DETAILS:
Title: {job.title}
Company: {job.company}
Description:
{job.description[:1500]}

CANDIDATE SKILLS: {skills_str}
{f"CANDIDATE BACKGROUND: {resume_summary}" if resume_summary else ""}

Generate a comprehensive interview question bank with EXACTLY 9 questions:
- 3 Behavioral questions (STAR method, soft skills, teamwork, conflict resolution)
- 3 Technical questions (specific to the role's technical requirements and the candidate's skill gaps)
- 3 Culture-fit / situational questions (company values, role expectations, motivation)

Return a strict JSON array of 9 question objects with EXACTLY these fields:
[
  {{
    "id": integer (1 to 9),
    "type": string (one of: "behavioral", "technical", "culture_fit"),
    "question": string (the full interview question text),
    "difficulty": string (one of: "easy", "medium", "hard"),
    "focus_area": string (brief tag like "leadership", "problem solving", "Python", "system design", etc.)
  }}
]
"""

        try:
            result = await generate_content(prompt, json_response=True, max_retries=2)
            if result and isinstance(result, list) and len(result) > 0:
                return result
            return self._fallback_questions(job)
        except Exception as e:
            logger.error(f"Failed to parse interview questions: {e}")
            return self._fallback_questions(job)

    async def evaluate_answer(
        self,
        question: str,
        candidate_answer: str,
        job: JobPosting,
        resume: Optional[Resume] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a candidate's answer to an interview question.
        Returns: score, strengths, improvements, model_answer, verdict
        """
        skills_str = ", ".join(resume.skills) if resume and resume.skills else ""

        prompt = f"""
You are an expert interview coach evaluating a candidate's response.

JOB: {job.title} at {job.company}
CANDIDATE SKILLS: {skills_str}

INTERVIEW QUESTION:
"{question}"

CANDIDATE'S ANSWER:
"{candidate_answer}"

Evaluate this answer rigorously but fairly. Return a strict JSON object:
{{
  "score": integer (0 to 100),
  "verdict": string (one of: "Excellent", "Good", "Needs Improvement", "Insufficient"),
  "strengths": array of strings (what the candidate did well — max 3 specific points),
  "improvements": array of strings (specific actionable improvements — max 3 points),
  "missing_points": array of strings (key points they should have mentioned but didn't — max 3),
  "model_answer": string (a strong example answer of 3-5 sentences demonstrating best practices for this specific question)
}}
"""

        try:
            result = await generate_content(prompt, json_response=True, max_retries=2)
            if not result:
                return self._fallback_evaluation(candidate_answer)
                
            required = ["score", "verdict", "model_answer"]
            for k in required:
                if k not in result:
                    raise ValueError(f"Missing key: {k}")
            return result
        except Exception as e:
            logger.error(f"Failed to parse evaluation response: {e}")
            return self._fallback_evaluation(candidate_answer)

    def _fallback_questions(self, job: JobPosting) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "type": "behavioral", "question": f"Tell me about a challenging project you worked on. How did you handle it?", "difficulty": "medium", "focus_area": "problem solving"},
            {"id": 2, "type": "behavioral", "question": "Describe a time you had to work with a difficult team member. What was the outcome?", "difficulty": "medium", "focus_area": "teamwork"},
            {"id": 3, "type": "behavioral", "question": "Give an example of when you took initiative on a project without being asked.", "difficulty": "easy", "focus_area": "leadership"},
            {"id": 4, "type": "technical", "question": f"What key technical skills make you a strong fit for the {job.title} role?", "difficulty": "medium", "focus_area": "technical skills"},
            {"id": 5, "type": "technical", "question": "Walk me through how you would approach debugging a production issue at 2 AM.", "difficulty": "hard", "focus_area": "system debugging"},
            {"id": 6, "type": "technical", "question": "How do you stay current with new technologies and industry trends?", "difficulty": "easy", "focus_area": "learning"},
            {"id": 7, "type": "culture_fit", "question": f"Why are you specifically interested in joining {job.company}?", "difficulty": "easy", "focus_area": "motivation"},
            {"id": 8, "type": "culture_fit", "question": "Where do you see yourself professionally in 3–5 years?", "difficulty": "medium", "focus_area": "career goals"},
            {"id": 9, "type": "culture_fit", "question": "What does your ideal work environment look like?", "difficulty": "easy", "focus_area": "culture fit"},
        ]

    def _fallback_evaluation(self, answer: str) -> Dict[str, Any]:
        raise ValueError("AI provider unavailable or returned invalid output. No score was generated; please retry.")


interview_coach = InterviewCoachService()
