import logging
import alembic.config
import alembic.command
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, users, sources, digests, pipeline
from app.pipeline.scheduler import start_scheduler, stop_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run database migrations and start/stop scheduler on startup/shutdown."""
    # 1. Database Migrations
    try:
        logger.info("Initializing database migrations...")
        alembic_cfg = alembic.config.Config("alembic.ini")
        alembic.command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations successfully executed.")
    except Exception as e:
        logger.error(f"Database migrations failed on startup: {e}. Please ensure DATABASE_URL is configured.")

    # 2. Scheduler
    try:
        logger.info("Starting background scheduler...")
        start_scheduler()
        logger.info("Background scheduler successfully started.")
    except Exception as e:
        logger.error(f"Failed to start scheduler on startup: {e}. Active schedules will not run until resolved.")

    yield
    stop_scheduler()

app = FastAPI(
    title="AI News Aggregator API",
    description=(
        "A multi-tenant SaaS platform that delivers personalized AI news digests. "
        "Users can configure their interests, sources, and email frequency."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────
# Allow the React frontend (dev & production endpoints)
import os

allowed_origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # CRA dev server
    "http://127.0.0.1:5173",
    "https://ai-news-curator-frontend.onrender.com",  # Production Render static site
]

env_origins = os.getenv("ALLOWED_ORIGINS")
if env_origins:
    allowed_origins.extend([o.strip() for o in env_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(sources.router)
app.include_router(digests.router)
app.include_router(pipeline.router)


# ── Health check ─────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "2.0.0"}
