import httpx
import json
import logging
import asyncio
from typing import Dict, Any, Optional, Union
from backend.core.config import settings

logger = logging.getLogger(__name__)

async def generate_content(
    prompt: str,
    json_response: bool = False,
    max_retries: int = 4,
    timeout: float = 30.0
) -> Union[str, Dict[str, Any]]:
    """
    Centralized function to call Gemini API with exponential backoff for rate limiting.
    Handles HTTP 429 and 503 by waiting and retrying.
    """
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured.")
        return {} if json_response else ""
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL or 'gemini-3.6-flash'}:generateContent?key={settings.GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    base_delay = 2.0
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(max_retries + 1):
            try:
                resp = await client.post(url, json=payload)
                
                # Success
                if resp.status_code == 200:
                    data = resp.json()
                    reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    
                    if json_response:
                        if reply.startswith("```json"):
                            reply = reply[7:-3].strip()
                        elif reply.startswith("```"):
                            reply = reply[3:-3].strip()
                        try:
                            return json.loads(reply)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse Gemini JSON output: {e}\nRaw: {reply}")
                            return {}
                    return reply
                
                # Rate Limit or Service Unavailable
                if resp.status_code in (429, 503):
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)  # 2, 4, 8, 16
                        logger.warning(f"Gemini API rate limited (HTTP {resp.status_code}). Retrying in {delay}s... (Attempt {attempt+1}/{max_retries})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.error(f"Gemini API rate limit exhausted after {max_retries} retries.")
                        return {} if json_response else ""
                
                # Other HTTP Errors
                logger.error(f"Gemini API Error {resp.status_code}: {resp.text[:200]}")
                return {} if json_response else ""
                
            except httpx.RequestError as e:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Gemini API network error: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Gemini API network error after retries: {e}")
                    return {} if json_response else ""
            except Exception as e:
                logger.error(f"Unexpected error in Gemini API call: {e}")
                return {} if json_response else ""
                
    return {} if json_response else ""
