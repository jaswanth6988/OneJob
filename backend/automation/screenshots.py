import os
import uuid
from datetime import datetime
from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

async def save_verification_screenshot(page, prefix: str = "apply_step") -> str:
    """
    Takes a full-page screenshot of the current Playwright page and saves it to storage.
    Returns the relative or absolute storage file path for database tracking and frontend display.
    """
    try:
        os.makedirs(settings.STORAGE_SCREENSHOTS, exist_ok=True)
        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
        filepath = os.path.join(settings.STORAGE_SCREENSHOTS, filename)
        
        # Take screenshot with playwright page object
        await page.screenshot(path=filepath, full_page=True)
        logger.info(f"Saved verification screenshot: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to capture verification screenshot: {e}", exc_info=True)
        return ""
