import os
import re
import asyncio
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout

from backend.core.config import settings
from backend.models.application import JobApplication, ApplicationStatus
from backend.models.job import JobPosting
from backend.models.resume import Resume
from backend.models.user import UserProfile
from backend.automation.ai_responder import ai_responder
from backend.automation.screenshots import save_verification_screenshot

logger = logging.getLogger(__name__)

class PlaywrightAutomationEngine:
    def __init__(self, headless: bool = True, timeout_ms: int = 45000):
        self.headless = headless
        self.timeout_ms = timeout_ms

    async def execute_application(
        self,
        application: JobApplication,
        job: JobPosting,
        user: UserProfile,
        resume: Optional[Resume] = None
    ) -> JobApplication:
        """
        Main entry point for executing an automated job application via browser bot.
        Modifies and returns the JobApplication object in place.
        """
        logger.info(f"Starting automation engine for Application {application.id} (Mode: {application.mode})")
        application.status = ApplicationStatus.APPLYING
        application.started_at = datetime.now(timezone.utc)
        await application.save()

        target_url = job.apply_url or job.url
        application.apply_url = target_url

        if not target_url:
            application.status = ApplicationStatus.FAILED
            application.error_log = "No valid apply URL found on job posting."
            application.completed_at = datetime.now(timezone.utc)
            await application.save()
            return application

        submitted_fields: Dict[str, Any] = {}
        ai_answers: List[Dict[str, str]] = []
        screenshots: List[str] = []

        async with async_playwright() as p:
            browser: Optional[Browser] = None
            try:
                try:
                    # Use system Microsoft Edge or Google Chrome from Program Files to comply with Windows Defender Application Control policies
                    browser = await p.chromium.launch(headless=self.headless, channel="msedge")
                    logger.info("Launched system Microsoft Edge for automation.")
                except Exception:
                    try:
                        browser = await p.chromium.launch(headless=self.headless, channel="chrome")
                        logger.info("Launched system Google Chrome for automation.")
                    except Exception:
                        browser = await p.chromium.launch(headless=self.headless)
                        logger.info("Launched bundled Playwright Chromium for automation.")
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
                )
                page = await context.new_page()
                page.set_default_timeout(self.timeout_ms)

                logger.info(f"Navigating to {target_url}...")
                await page.goto(target_url, wait_until="domcontentloaded")
                await asyncio.sleep(2) # Give dynamic frameworks a moment to render

                # 1. Take initial screenshot
                init_shot = await save_verification_screenshot(page, f"app_{application.id}_init")
                if init_shot:
                    screenshots.append(init_shot)

                # 2. Extract and match common inputs
                inputs = await page.query_selector_all("input:not([type='hidden']):not([type='submit']):not([type='button']), textarea, select")
                logger.info(f"Found {len(inputs)} interactive form elements on page.")

                for elem in inputs:
                    try:
                        tag = await elem.evaluate("node => node.tagName.toLowerCase()")
                        input_type = await elem.evaluate("node => node.type || ''")
                        name = await elem.evaluate("node => node.name || ''")
                        id_attr = await elem.evaluate("node => node.id || ''")
                        placeholder = await elem.evaluate("node => node.placeholder || ''")
                        aria_label = await elem.evaluate("node => node.getAttribute('aria-label') || ''")

                        # Try to find associated <label>
                        label_text = aria_label or placeholder
                        if id_attr:
                            label_elem = await page.query_selector(f"label[for='{id_attr}']")
                            if label_elem:
                                label_text = (await label_elem.inner_text()).strip()
                        
                        field_identifier = (label_text or name or id_attr).lower()
                        if not field_identifier:
                            continue

                        logger.debug(f"Evaluating field: {field_identifier} (Type: {input_type})")

                        # Handle File Uploads (Resume / Cover Letter)
                        if input_type == "file":
                            if resume and resume.file_path and os.path.exists(resume.file_path):
                                logger.info(f"Uploading resume file: {resume.file_path}")
                                await elem.set_input_files(resume.file_path)
                                submitted_fields["Resume File"] = os.path.basename(resume.file_path)
                            continue

                        # Handle Standard Contact Information Fields
                        filled_val = None
                        if any(k in field_identifier for k in ["first name", "firstname", "fname"]):
                            filled_val = getattr(user, "first_name", "Alex")
                        elif any(k in field_identifier for k in ["last name", "lastname", "lname"]):
                            filled_val = getattr(user, "last_name", "Developer")
                        elif any(k in field_identifier for k in ["full name", "fullname", "name"]):
                            filled_val = f"{getattr(user, 'first_name', 'Alex')} {getattr(user, 'last_name', 'Developer')}".strip()
                        elif "email" in field_identifier:
                            filled_val = getattr(user, "email", "applicant@example.com")
                        elif any(k in field_identifier for k in ["phone", "tel", "mobile"]):
                            filled_val = getattr(user, "phone", "+1 555 0199")
                        elif any(k in field_identifier for k in ["linkedin", "linked in"]):
                            filled_val = getattr(user, "linkedin_url", "https://linkedin.com/in/applicant-profile")
                        elif any(k in field_identifier for k in ["github", "git", "portfolio", "website", "url"]):
                            filled_val = getattr(user, "portfolio_url", "https://github.com/applicant")

                        if filled_val:
                            await elem.fill(str(filled_val))
                            submitted_fields[label_text or name or id_attr] = str(filled_val)
                            continue

                        # Handle Open-ended screening textareas or long text questions via Gemini
                        if tag == "textarea" or any(q in field_identifier for q in ["why", "experience", "describe", "salary", "summary", "cover letter", "about you", "expectations"]):
                            question_str = label_text or placeholder or name
                            ai_val = await ai_responder.generate_answer(question_str, job, resume)
                            await elem.fill(ai_val)
                            submitted_fields[question_str] = ai_val
                            ai_answers.append({"question": question_str, "answer": ai_val})
                    
                    except Exception as field_err:
                        logger.warning(f"Skipped filling element due to error: {field_err}")

                # 3. Take pre-submit verification screenshot
                pre_submit_shot = await save_verification_screenshot(page, f"app_{application.id}_filled")
                if pre_submit_shot:
                    screenshots.append(pre_submit_shot)

                # 4. Handle Submission Mode
                if application.mode == "DRY_RUN":
                    logger.info("DRY_RUN Mode: Stopping right before final submit click.")
                    application.status = ApplicationStatus.SUBMITTED
                    submitted_fields["Execution_Notice"] = "Dry-Run verification successful. Form filled without final button press."
                else:
                    logger.info("LIVE Mode: Attempting to locate and press Submit button...")
                    submit_btn = await page.query_selector("button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Apply'), button:has-text('Send')")
                    if submit_btn:
                        await submit_btn.click()
                        await asyncio.sleep(4) # Wait for confirmation message
                        post_shot = await save_verification_screenshot(page, f"app_{application.id}_submitted")
                        if post_shot:
                            screenshots.append(post_shot)
                        application.status = ApplicationStatus.SUBMITTED
                    else:
                        logger.warning("Could not find unambiguous submit button. Requires manual verification.")
                        application.status = ApplicationStatus.REQUIRES_MANUAL_INTERVENTION

            except PlaywrightTimeout as te:
                logger.error(f"Playwright timeout navigating or filling {target_url}: {te}")
                application.status = ApplicationStatus.FAILED
                application.error_log = f"Timeout error: {str(te)}"
                if browser and page:
                    err_shot = await save_verification_screenshot(page, f"app_{application.id}_timeout")
                    if err_shot:
                        screenshots.append(err_shot)
            except Exception as ex:
                logger.error(f"Unexpected automation error on {target_url}: {ex}", exc_info=True)
                application.status = ApplicationStatus.FAILED
                application.error_log = f"Automation exception: {str(ex)}"
            finally:
                if browser:
                    await browser.close()

        application.submitted_fields = submitted_fields
        application.ai_answers = ai_answers
        application.screenshots = screenshots
        application.completed_at = datetime.now(timezone.utc)
        application.updated_at = datetime.now(timezone.utc)
        
        await application.save()
        logger.info(f"Automation execution complete for Application {application.id}. Status: {application.status}")
        return application

automation_engine = PlaywrightAutomationEngine()
