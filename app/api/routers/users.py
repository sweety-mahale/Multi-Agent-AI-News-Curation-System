from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional

from app.api.dependencies import get_db, get_current_user
from app.database.models import User
from app.database.repository import Repository

router = APIRouter(prefix="/users", tags=["Users"])


# ── Schemas ──────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    id: str
    name: str
    title: Optional[str]
    background: Optional[str]
    interests: list[str]
    preferences: dict
    expertise_level: str


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    background: Optional[str] = None
    interests: Optional[list[str]] = None
    preferences: Optional[dict] = None
    expertise_level: Optional[str] = None


class EmailSettingsResponse(BaseModel):
    email_address: str
    frequency: str
    delivery_hour: int
    delivery_day: Optional[str]
    top_n: int
    is_active: bool


class EmailSettingsUpdateRequest(BaseModel):
    email_address: Optional[EmailStr] = None
    frequency: Optional[str] = None      # "daily" | "weekly"
    delivery_hour: Optional[int] = None  # 0-23 UTC
    delivery_day: Optional[str] = None   # "monday" etc. (weekly only)
    top_n: Optional[int] = None


class MeResponse(BaseModel):
    id: str
    email: str
    profile: Optional[ProfileResponse]
    email_settings: Optional[EmailSettingsResponse]


# ── Endpoints ────────────────────────────────────────────────

@router.get("/me", response_model=MeResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authenticated user's full profile and settings."""
    repo = Repository(db)
    profile = repo.get_user_profile(current_user.id)
    settings = repo.get_user_email_settings(current_user.id)

    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        profile=ProfileResponse(
            id=profile.id,
            name=profile.name,
            title=profile.title,
            background=profile.background,
            interests=profile.interests or [],
            preferences=profile.preferences or {},
            expertise_level=profile.expertise_level,
        ) if profile else None,
        email_settings=EmailSettingsResponse(
            email_address=settings.email_address,
            frequency=settings.frequency,
            delivery_hour=settings.delivery_hour,
            delivery_day=settings.delivery_day,
            top_n=settings.top_n,
            is_active=settings.is_active,
        ) if settings else None,
    )


@router.put("/me/profile", response_model=ProfileResponse)
def update_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the user's AI interest profile."""
    repo = Repository(db)
    updates = body.model_dump(exclude_none=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    profile = repo.update_user_profile(current_user.id, **updates)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        title=profile.title,
        background=profile.background,
        interests=profile.interests or [],
        preferences=profile.preferences or {},
        expertise_level=profile.expertise_level,
    )


@router.put("/me/settings", response_model=EmailSettingsResponse)
def update_email_settings(
    body: EmailSettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update email delivery preferences (frequency, timing, top_n)."""
    repo = Repository(db)
    updates = body.model_dump(exclude_none=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    # Validate frequency
    if "frequency" in updates and updates["frequency"] not in ("daily", "weekly"):
        raise HTTPException(status_code=400, detail="frequency must be 'daily' or 'weekly'.")

    # Validate delivery_hour
    if "delivery_hour" in updates and not (0 <= updates["delivery_hour"] <= 23):
        raise HTTPException(status_code=400, detail="delivery_hour must be 0-23.")

    settings = repo.update_user_email_settings(current_user.id, **updates)
    if not settings:
        raise HTTPException(status_code=404, detail="Email settings not found.")

    return EmailSettingsResponse(
        email_address=settings.email_address,
        frequency=settings.frequency,
        delivery_hour=settings.delivery_hour,
        delivery_day=settings.delivery_day,
        top_n=settings.top_n,
        is_active=settings.is_active,
    )
