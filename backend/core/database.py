from typing import Any
import motor.motor_asyncio
from beanie import init_beanie
from backend.core.config import settings

# Import all models to register with Beanie
from backend.models.user import UserProfile
from backend.models.resume import Resume
from backend.models.job import JobPosting
from backend.models.application import ApplicationAttempt
from backend.models.manual_review import ManualReviewItem
from backend.models.ai_event import AIEventLog

# Global db client
class Database:
    client: motor.motor_asyncio.AsyncIOMotorClient = None

db = Database()

async def init_db() -> None:
    """Initialize the MongoDB connection and Beanie ODM."""
    db.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URL)
    
    await init_beanie(
        database=db.client[settings.MONGO_DB],
        document_models=[
            UserProfile,
            Resume,
            JobPosting,
            ApplicationAttempt,
            ManualReviewItem,
            AIEventLog,
        ],
    )

async def close_db() -> None:
    """Close the MongoDB connection."""
    if db.client:
        db.client.close()

def get_database() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Dependency to get the database instance."""
    return db.client[settings.MONGO_DB]
