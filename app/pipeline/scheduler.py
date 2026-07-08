"""
Persistent APScheduler
======================
Schedules the global pipeline (once per day) and per-user curation
jobs (based on each user's delivery_hour + frequency settings).

Uses a SQLAlchemy job store so all scheduled jobs survive server
restarts and Render.com deploys.
"""
import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

# Resolve DATABASE_URL (same logic as alembic/env.py)
def _get_db_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if not url:
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "ai_news_aggregator")
        url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return url


def _create_scheduler() -> AsyncIOScheduler:
    """Create an APScheduler backed by PostgreSQL for job persistence."""
    db_url = _get_db_url()
    jobstores = {
        "default": SQLAlchemyJobStore(url=db_url, tablename="apscheduler_jobs")
    }
    scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="UTC")
    return scheduler


# Singleton scheduler instance (shared across the FastAPI app)
scheduler = _create_scheduler()


# ── Global pipeline job ──────────────────────────────────────────

def _global_pipeline_job():
    """Wrapper for the APScheduler thread to call the global pipeline."""
    from app.pipeline.global_runner import run_global_pipeline
    logger.info("[SCHEDULER] Global pipeline triggered")
    run_global_pipeline(hours=25)  # 25h window to catch any late articles


def schedule_global_pipeline(hour: int = 5):
    """
    Schedule the global scraping + summarization pipeline.
    Default: runs at 5 AM UTC every day (before user emails go out).
    """
    job_id = "global_pipeline"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    scheduler.add_job(
        _global_pipeline_job,
        trigger=CronTrigger(hour=hour, minute=0, timezone="UTC"),
        id=job_id,
        name="Global Pipeline (scrape + summarize)",
        replace_existing=True,
        misfire_grace_time=3600,  # Allow up to 1h late if server was down
    )
    logger.info(f"[SCHEDULER] Global pipeline scheduled at {hour:02d}:00 UTC daily")


# ── Per-user pipeline jobs ───────────────────────────────────────

def run_user_pipeline_job(user_id: str):
    """Module-level job function that runs the user pipeline."""
    from app.pipeline.user_runner import run_user_pipeline
    logger.info(f"[SCHEDULER] User pipeline triggered for {user_id}")
    run_user_pipeline(user_id, hours=25)


def schedule_user_job(user_id: str, frequency: str, delivery_hour: int, delivery_day: str = None):
    """
    Register or update the delivery schedule for a single user.

    Args:
        user_id: The user's UUID.
        frequency: "daily" or "weekly".
        delivery_hour: 0–23 UTC hour of delivery.
        delivery_day: Day name for weekly (e.g. "monday"). Ignored for daily.
    """
    job_id = f"user_{user_id}"

    if frequency == "weekly" and delivery_day:
        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
        }
        day_of_week = day_map.get(delivery_day.lower(), 0)
        trigger = CronTrigger(
            day_of_week=day_of_week,
            hour=delivery_hour,
            minute=0,
            timezone="UTC",
        )
        schedule_label = f"weekly on {delivery_day} at {delivery_hour:02d}:00 UTC"
    else:
        trigger = CronTrigger(hour=delivery_hour, minute=0, timezone="UTC")
        schedule_label = f"daily at {delivery_hour:02d}:00 UTC"

    scheduler.add_job(
        run_user_pipeline_job,
        args=[user_id],
        trigger=trigger,
        id=job_id,
        name=f"User digest: {user_id}",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    logger.info(f"[SCHEDULER] User {user_id} scheduled {schedule_label}")


def remove_user_job(user_id: str):
    """Remove the scheduled job for a user (e.g., when they deactivate)."""
    job_id = f"user_{user_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"[SCHEDULER] Removed job for user {user_id}")


def load_all_user_schedules():
    """
    Load all active users from the DB and register their delivery schedules.
    Called once at server startup after existing jobs are cleared.
    """
    from app.database.repository import Repository
    repo = Repository()
    users = repo.get_all_active_users()
    repo.session.close()

    logger.info(f"[SCHEDULER] Loading schedules for {len(users)} active users")

    for user in users:
        settings = None
        repo2 = Repository()
        try:
            settings = repo2.get_user_email_settings(user.id)
        finally:
            repo2.session.close()

        if settings and settings.is_active:
            schedule_user_job(
                user_id=user.id,
                frequency=settings.frequency,
                delivery_hour=settings.delivery_hour,
                delivery_day=settings.delivery_day,
            )

    logger.info("[SCHEDULER] All user schedules loaded")


def start_scheduler():
    """Start the scheduler and register all jobs. Called in FastAPI startup."""
    schedule_global_pipeline(hour=5)  # Global pipeline runs at 5 AM UTC
    load_all_user_schedules()
    scheduler.start()
    logger.info("[SCHEDULER] Scheduler started")


def stop_scheduler():
    """Gracefully shut down the scheduler. Called in FastAPI shutdown."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[SCHEDULER] Scheduler stopped")
