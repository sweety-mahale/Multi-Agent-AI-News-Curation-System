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
    from app.pipeline.global_runner import run_global_pipeline
    from app.database.connection import get_session
    from app.database.models import ArticleSummary
    from datetime import datetime, timedelta

    logger.info(f"[PIPELINE] ===== Manual trigger START for user {user_id} =====")

    # Self-healing: if database is completely empty, scrape globally first
    session = get_session()
    try:
        summary_count = session.query(ArticleSummary).count()
        logger.info(f"[PIPELINE] Total article_summaries in DB: {summary_count}")

        # Also log the newest summary creation time
        if summary_count > 0:
            newest = session.query(ArticleSummary).order_by(ArticleSummary.created_at.desc()).first()
            cutoff_check = datetime.utcnow() - timedelta(hours=180)
            logger.info(f"[PIPELINE] Newest summary created_at: {newest.created_at} | 180h cutoff: {cutoff_check}")
            visible = session.query(ArticleSummary).filter(ArticleSummary.created_at >= cutoff_check).count()
            logger.info(f"[PIPELINE] Summaries visible within 180h window: {visible}")

        if summary_count == 0:
            logger.info("[PIPELINE] DB empty — launching global scrape...")
            run_global_pipeline(hours=24)
            logger.info("[PIPELINE] Global scrape finished.")
    except Exception as e:
        logger.error(f"[PIPELINE] Error in pre-check/self-healing: {e}", exc_info=True)
    finally:
        session.close()

    logger.info(f"[PIPELINE] Calling run_user_pipeline for user {user_id} with hours=180")
    result = run_user_pipeline(user_id, hours=180)
    logger.info(f"[PIPELINE] run_user_pipeline result: {result}")

    if result.get("success"):
        logger.info(f"[PIPELINE] ✅ User {user_id}: sent {result.get('articles_sent', 0)} articles")
    elif result.get("skipped"):
        logger.warning(f"[PIPELINE] ⚠️ User {user_id}: SKIPPED — {result.get('reason')}")
    else:
        logger.error(f"[PIPELINE] ❌ User {user_id}: FAILED — {result.get('error')}")
    logger.info(f"[PIPELINE] ===== Manual trigger END for user {user_id} =====")


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
