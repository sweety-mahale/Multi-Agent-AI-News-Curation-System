from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.api.dependencies import get_db, get_current_user
from app.database.models import User
from app.database.repository import Repository

router = APIRouter(prefix="/digests", tags=["Digests"])


# ── Schemas ──────────────────────────────────────────────────

class DigestItemResponse(BaseModel):
    summary_id: str
    rank: Optional[int]
    relevance_score: Optional[float]
    sent_at: datetime
    title: str
    summary: str
    url: str
    article_type: str


# ── Endpoints ────────────────────────────────────────────────

@router.get("", response_model=list[DigestItemResponse])
def get_digest_history(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the most recent digest items sent to the current user.
    Used by the frontend dashboard to show digest history.
    """
    repo = Repository(db)
    items = repo.get_user_sent_history(current_user.id, limit=limit)
    return [DigestItemResponse(**item) for item in items]
