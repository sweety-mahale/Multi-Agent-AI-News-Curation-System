from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.api.dependencies import get_db, get_current_user
from app.database.models import User
from app.database.repository import Repository

router = APIRouter(prefix="/sources", tags=["Sources"])


# ── Schemas ──────────────────────────────────────────────────

class SourceResponse(BaseModel):
    id: str
    source_type: str
    name: str
    url: str
    is_active: bool


class AddSourceRequest(BaseModel):
    source_type: str   # "youtube" | "rss"
    name: str          # Display name e.g. "Two Minute Papers"
    url: str           # YouTube channel ID or RSS feed URL


# ── Endpoints ────────────────────────────────────────────────

@router.get("", response_model=list[SourceResponse])
def list_sources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all active news sources configured by the current user."""
    repo = Repository(db)
    sources = repo.get_user_sources(current_user.id)
    return [
        SourceResponse(
            id=s.id,
            source_type=s.source_type,
            name=s.name,
            url=s.url,
            is_active=s.is_active,
        )
        for s in sources
    ]


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def add_source(
    body: AddSourceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a YouTube channel or RSS feed as a personal news source."""
    if body.source_type not in ("youtube", "rss"):
        raise HTTPException(
            status_code=400,
            detail="source_type must be 'youtube' or 'rss'.",
        )

    if not body.url.strip():
        raise HTTPException(status_code=400, detail="url cannot be empty.")

    repo = Repository(db)
    source = repo.create_user_source(
        user_id=current_user.id,
        source_type=body.source_type,
        name=body.name,
        url=body.url.strip(),
    )
    return SourceResponse(
        id=source.id,
        source_type=source.source_type,
        name=source.name,
        url=source.url,
        is_active=source.is_active,
    )


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_source(
    source_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a user source (soft delete — sets is_active=False)."""
    repo = Repository(db)
    deleted = repo.delete_user_source(source_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Source not found or does not belong to this user.",
        )
