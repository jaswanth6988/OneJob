import os
import json
import logging
from typing import Any
import motor.motor_asyncio
from beanie import init_beanie
from backend.core.config import settings

# Import all models to register with Beanie
from backend.models.user import UserProfile
from backend.models.resume import Resume
from backend.models.job import JobPosting
from backend.models.application import JobApplication
from backend.models.manual_review import ManualReviewItem
from backend.models.ai_event import AIEventLog

logger = logging.getLogger(__name__)

# Global db client
class Database:
    client: Any = None

db = Database()

async def init_db() -> None:
    """Initialize the MongoDB connection and Beanie ODM, falling back to in-memory mock if live Mongo is unavailable."""
    if db.client is not None:
        return
    models = [
        UserProfile,
        Resume,
        JobPosting,
        JobApplication,
        ManualReviewItem,
        AIEventLog,
    ]
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=2000
        )
        await client.admin.command("ping")
        db.client = client
        await init_beanie(
            database=db.client[settings.MONGO_DB],
            document_models=models,
        )
        logger.info(f"Connected to live MongoDB at {settings.MONGO_URL}")
    except Exception as exc:
        logger.warning(f"Live MongoDB not reachable ({exc}). Falling back to in-memory MongoDB mock (mongomock_motor).")
        from mongomock_motor import AsyncMongoMockClient
        db.client = AsyncMongoMockClient()
        await init_beanie(
            database=db.client[settings.MONGO_DB],
            document_models=models,
        )
        await _seed_mock_jobs_if_empty()

async def _seed_mock_jobs_if_empty():
    try:
        user = await UserProfile.find_one(UserProfile.email == "demo@example.com")
        if not user:
            from backend.core.security import get_password_hash
            user = UserProfile(
                email="demo@example.com",
                hashed_password=get_password_hash("Password123!"),
                name="Demo User"
            )
            await user.insert()
            logger.info("Seeded default demo user (demo@example.com)")

        count = await JobPosting.count()
        if count == 0:
            test_json_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "test.json"
            )
            if os.path.exists(test_json_path):
                from backend.connectors.remoteok import RemoteOKConnector
                connector = RemoteOKConnector()
                with open(test_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                jobs_to_insert = []
                for raw in data:
                    if raw.get("id") and raw.get("position") and raw.get("company"):
                        job = connector.normalize_job(raw)
                        jobs_to_insert.append(job)
                if jobs_to_insert:
                    await JobPosting.insert_many(jobs_to_insert)
                    logger.info(f"Seeded {len(jobs_to_insert)} mock job postings into in-memory database.")
    except Exception as e:
        logger.warning(f"Error seeding mock jobs: {e}")

async def close_db() -> None:
    """Close the MongoDB connection."""
    if db.client:
        db.client.close()

def get_database():
    """Dependency to get the database instance."""
    return db.client[settings.MONGO_DB]
