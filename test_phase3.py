import os
import asyncio
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from backend.models.application import ApplicationStatus
from backend.automation.engine import automation_engine

# Mock classes to allow 100% offline testing of Playwright browser engine & Gemini REST without requiring MongoDB running
@dataclass
class MockUserProfile:
    email: str
    first_name: str
    last_name: str
    phone: str
    linkedin_url: str
    portfolio_url: str

@dataclass
class MockResume:
    title: str
    file_path: str
    skills: List[str]
    parsed_text: str

@dataclass
class MockJob:
    title: str
    company: str
    description: str
    apply_url: str
    url: str

@dataclass
class MockApplication:
    id: str = "6a70d5230dda6a18b58d13fe"
    mode: str = "LIVE"
    status: Any = ApplicationStatus.QUEUED
    apply_url: str = ""
    error_log: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    submitted_fields: Dict[str, Any] = field(default_factory=dict)
    ai_answers: List[Dict[str, str]] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)

    async def save(self):
        pass

async def main():
    print("=== Phase 3 Verification: Standalone Playwright & Gemini AI Auto-Applier ===")
    
    user = MockUserProfile(
        email="alex.developer@ai-job-portal.ai",
        first_name="Alex",
        last_name="Mercer",
        phone="+1 (415) 555-0188",
        linkedin_url="https://linkedin.com/in/alexmercer-ai",
        portfolio_url="https://github.com/alexmercer"
    )

    dummy_resume_path = os.path.abspath("storage/demo_resume.pdf")
    os.makedirs("storage", exist_ok=True)
    with open(dummy_resume_path, "w") as f:
        f.write("Demo PDF Resume Content for Alex Mercer - Senior Python & React AI Engineer.")
    
    resume = MockResume(
        title="Alex Mercer - Lead AI Resume",
        file_path=dummy_resume_path,
        skills=["Python", "React", "Next.js", "Gemini AI", "Playwright", "MongoDB", "FastAPI"],
        parsed_text="Experienced Senior AI Engineer specializing in LLM applications, Python Fast API, Next.js, and browser automation using Playwright and Google Gemini."
    )

    mock_url = f"file:///{os.path.abspath('test_mock_form.html').replace(chr(92), '/')}"
    job = MockJob(
        title="Senior AI Engineer",
        company="Acme AI Corp",
        apply_url=mock_url,
        url=mock_url,
        description="We are seeking a proactive Full Stack AI engineer experienced in large language models, autonomous AI agents, Python backend infrastructures, and highly functional user interfaces."
    )

    app = MockApplication(mode="LIVE", apply_url=mock_url)

    print(f"Target Apply URL: {mock_url}")
    print("\nLaunching automated Playwright browser bot & querying Gemini REST...")

    # Run the automation engine!
    updated_app = await automation_engine.execute_application(app, job, user, resume) # type: ignore

    print("\n================= EXECUTION RESULTS ==================")
    print(f"Final Application Status: {updated_app.status}")
    print(f"Target Apply URL:         {updated_app.apply_url}")
    print("\n--- Submitted Form Fields & Profile Values ---")
    for k, v in updated_app.submitted_fields.items():
        print(f"  [{k}]: {v}")

    print("\n--- Gemini AI Screening Answers ---")
    if not updated_app.ai_answers:
        print("  None generated.")
    for qa in updated_app.ai_answers:
        print(f"  Q: {qa['question']}")
        print(f"  A: {qa['answer']}\n")

    print(f"--- Verification Screenshots Saved ({len(updated_app.screenshots)}) ---")
    for shot in updated_app.screenshots:
        print(f"  📸 {shot}")
    print("======================================================")

if __name__ == "__main__":
    asyncio.run(main())
