from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, users, sources, digests, pipeline
from app.pipeline.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start scheduler on startup, shut it down cleanly on exit."""
    start_scheduler()
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
# Allow the React frontend (dev: port 5173, prod: same domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # CRA dev server
        "http://127.0.0.1:5173",
    ],
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
