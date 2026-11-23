"""At-most-once claim: never blindly resubmit an uncertain external application."""
import logging
from backend.core.celery_app import celery_app, run_async
from backend.core.database import init_db, close_db
from backend.models.application import JobApplication, ApplicationStatus
from backend.models.job import JobPosting
from backend.models.resume import Resume
from backend.models.user import UserProfile
from backend.automation.engine import automation_engine
from beanie import PydanticObjectId

logger = logging.getLogger(__name__)

def linked_id(value):
    return value.ref.id if hasattr(value, 'ref') else value.id

async def _async_apply_to_job(application_id: str):
    await init_db()
    try:
        result = await JobApplication.get_motor_collection().update_one(
            {'_id':PydanticObjectId(application_id),'status':'QUEUED'}, {'$set':{'status':'APPLYING'}})
        if not result.modified_count: return 'Already claimed or completed'
        app = await JobApplication.get(application_id)
        job = await JobPosting.get(linked_id(app.job_id))
        user = await UserProfile.get(linked_id(app.user_id))
        resume = await Resume.get(linked_id(app.resume_id)) if app.resume_id else None
        if not job or not user or not resume or linked_id(resume.user_id) != user.id:
            raise ValueError('Application records could not be resolved for this account')
        await automation_engine.execute_application(app, job, user, resume)
        return app.status.value
    except Exception as exc:
        app = await JobApplication.get(application_id)
        if app:
            app.status = ApplicationStatus.REQUIRES_MANUAL_INTERVENTION
            app.error_log = 'Execution interrupted. Review the destination before creating another attempt.'
            await app.save()
        logger.exception('Application interrupted')
        return 'Manual review required'
    finally:
        await close_db()

@celery_app.task(name='backend.workers.auto_applier.apply_to_job')
def apply_to_job(application_id: str):
    return run_async(_async_apply_to_job(application_id))
