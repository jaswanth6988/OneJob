from typing import Optional
from datetime import datetime, timezone
from pydantic import Field
from beanie import Document

class AIEventLog(Document):
    entity_type: str  # job, resume, application, review
    entity_id: str
    event_type: str   # MATCH_ANALYSIS, ATS_SCORING, ANSWER_GENERATION, FAILURE_DIAGNOSIS, SKILL_GAP, RESUME_IMPROVEMENT
    
    prompt_name: str
    input_summary: str = Field(max_length=500)
    output_summary: str = Field(max_length=1000)
    
    confidence: Optional[float] = None
    tokens_used: Optional[int] = None
    duration_ms: Optional[int] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "ai_event_logs"
