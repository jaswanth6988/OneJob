import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.config import settings
from enum import Enum
import os

class LogSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

# Thread-local storage equivalent for correlation IDs in async context
import contextvars
correlation_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="")

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
        token = correlation_id_ctx_var.set(correlation_id)
        
        # Add to request state for easy access if needed
        request.state.correlation_id = correlation_id
        
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        
        correlation_id_ctx_var.reset(token)
        return response

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": settings.APP_NAME,
            "module": record.module,
            "message": record.getMessage(),
            "correlation_id": correlation_id_ctx_var.get(),
        }

        # Add extra fields if they exist
        extra_fields = ["job_id", "attempt_id", "resume_id", "step", "error_code", "screenshot_path", "retry_count"]
        for field in extra_fields:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)

        if record.exc_info:
            log_data["stack_trace"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def get_logger(name: str) -> logging.Logger:
    """Get a structured JSON logger."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        logger.addHandler(console_handler)
        
        # File handler
        os.makedirs(settings.STORAGE_LOGS, exist_ok=True)
        log_file = os.path.join(settings.STORAGE_LOGS, "app.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
        
    return logger

logger = get_logger(__name__)
