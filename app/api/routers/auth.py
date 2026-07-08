from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.database.repository import Repository
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Request / Response schemas ───────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    title: str = ""
    background: str = ""
    interests: list[str] = []
    expertise_level: str = "Intermediate"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    name: str


# ── Endpoints ────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account with a profile and default email settings."""
    repo = Repository(db)

    # Check for duplicate email
    if repo.get_user_by_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Create user
    user = repo.create_user(
        email=body.email,
        hashed_password=hash_password(body.password),
    )

    # Create their profile
    repo.create_user_profile(
        user_id=user.id,
        name=body.name,
        title=body.title,
        background=body.background,
        interests=body.interests,
        expertise_level=body.expertise_level,
    )

    # Create default email settings (daily at 8 AM UTC, 10 articles)
    repo.create_user_email_settings(
        user_id=user.id,
        email_address=body.email,
        frequency="daily",
        delivery_hour=8,
        top_n=10,
    )

    return UserResponse(id=user.id, email=user.email, name=body.name)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate and return a JWT access token."""
    repo = Repository(db)
    user = repo.get_user_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    token = create_access_token(data={"sub": user.id})
    return TokenResponse(access_token=token)
