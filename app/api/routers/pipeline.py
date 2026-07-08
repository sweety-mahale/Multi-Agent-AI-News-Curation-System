import logging
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.database.models import User
from app.pipeline.scheduler import schedule_user_job

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


class PipelineRunResponse(BaseModel):
    message: str
    user_id: str


def _run_pipeline_background(user_id: str):
    """Background task: runs per-user curation + email pipeline."""
    from app.pipeline.user_runner import run_user_pipeline
    logger.info(f"[PIPELINE] Manual trigger for user {user_id}")
    result = run_user_pipeline(user_id, hours=180)
    if result.get("success"):
        logger.info(f"[PIPELINE] User {user_id}: sent {result.get('articles_sent', 0)} articles")
    elif result.get("skipped"):
        logger.info(f"[PIPELINE] User {user_id}: skipped — {result.get('reason')}")
    else:
        logger.error(f"[PIPELINE] User {user_id}: failed — {result.get('error')}")


@router.post("/run", response_model=PipelineRunResponse)
def trigger_pipeline(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Manually trigger a digest pipeline run for the current user.
    The run happens in the background — endpoint returns immediately.
    """
    background_tasks.add_task(_run_pipeline_background, current_user.id)
    return PipelineRunResponse(
        message="Pipeline run started. You will receive your digest email shortly.",
        user_id=current_user.id,
    )


@router.post("/reschedule", response_model=PipelineRunResponse)
def reschedule_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reload this user's delivery schedule from their current email settings.
    Call this after updating frequency or delivery_hour via PUT /users/me/settings.
    """
    from app.database.repository import Repository
    repo = Repository(db)
    settings = repo.get_user_email_settings(current_user.id)

    if not settings or not settings.is_active:
        return PipelineRunResponse(
            message="Email delivery is disabled. Enable it in settings first.",
            user_id=current_user.id,
        )

    schedule_user_job(
        user_id=current_user.id,
        frequency=settings.frequency,
        delivery_hour=settings.delivery_hour,
        delivery_day=settings.delivery_day,
    )

    return PipelineRunResponse(
        message=f"Schedule updated: {settings.frequency} at {settings.delivery_hour:02d}:00 UTC.",
        user_id=current_user.id,
    )
