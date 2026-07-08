from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column, String, DateTime, Text, Boolean,
    Integer, Float, ForeignKey, UniqueConstraint, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ─────────────────────────────────────────────
#  GLOBAL SHARED TABLES (no user_id — shared article pool)
# ─────────────────────────────────────────────

class YouTubeVideo(Base):
    """Shared pool of scraped YouTube videos (global, not per-user)."""
    __tablename__ = "youtube_videos"

    video_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    description = Column(Text)
    transcript = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class OpenAIArticle(Base):
    """Shared pool of scraped OpenAI RSS articles (global, not per-user)."""
    __tablename__ = "openai_articles"

    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnthropicArticle(Base):
    """Shared pool of scraped Anthropic RSS articles (global, not per-user)."""
    __tablename__ = "anthropic_articles"

    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    markdown = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ArticleSummary(Base):
    """
    LLM-generated summary for a single article.
    Generated ONCE per article and shared across all users.
    Replaces the old single-user 'Digest' table.
    """
    __tablename__ = "article_summaries"

    # Format: "article_type:article_id" e.g. "youtube:abc123"
    id = Column(String, primary_key=True)
    article_type = Column(String, nullable=False)   # "youtube", "openai", "anthropic"
    article_id = Column(String, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Reverse relationship: which users have received this summary
    sent_items = relationship("UserSentItem", back_populates="summary")


# ─────────────────────────────────────────────
#  PER-USER TABLES
# ─────────────────────────────────────────────

class User(Base):
    """Core user account table."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    sources = relationship("UserSource", back_populates="user")
    email_settings = relationship("UserEmailSettings", back_populates="user", uselist=False)
    sent_items = relationship("UserSentItem", back_populates="user")


class UserProfile(Base):
    """
    Each user's personalized AI interest profile.
    Replaces the hardcoded app/profiles/user_profile.py file.
    """
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String, nullable=False)
    title = Column(String, nullable=True)
    background = Column(Text, nullable=True)
    # JSON list of interest strings e.g. ["LLMs", "RAG systems", ...]
    interests = Column(JSON, nullable=False, default=list)
    # JSON dict of preference flags e.g. {"prefer_practical": true, ...}
    preferences = Column(JSON, nullable=False, default=dict)
    expertise_level = Column(String, default="Intermediate")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class UserSource(Base):
    """
    A user-configured news source (YouTube channel or RSS feed).
    Sources unique to one user are scraped per-user.
    Sources shared by many users are promoted to the global scraping pool.
    """
    __tablename__ = "user_sources"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    source_type = Column(String, nullable=False)  # "youtube" | "rss"
    name = Column(String, nullable=False)          # Display name
    url = Column(String, nullable=False)           # RSS URL or YouTube channel ID
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sources")


class UserEmailSettings(Base):
    """Email delivery preferences for each user."""
    __tablename__ = "user_email_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    email_address = Column(String, nullable=False)   # Where to send the digest
    frequency = Column(String, default="daily")      # "daily" | "weekly"
    delivery_hour = Column(Integer, default=8)       # 0–23 UTC hour
    # For weekly: "monday", "tuesday", etc. Null for daily.
    delivery_day = Column(String, nullable=True)
    top_n = Column(Integer, default=10)              # How many articles per digest
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="email_settings")


class UserSentItem(Base):
    """
    Tracks which article summaries were sent to which user and when.
    Replaces the old sent_at field on the Digest table.
    Ensures each user only receives each article once.
    """
    __tablename__ = "user_sent_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    summary_id = Column(String, ForeignKey("article_summaries.id"), nullable=False)
    rank = Column(Integer, nullable=True)
    relevance_score = Column(Float, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)

    # Each user can only receive each summary once
    __table_args__ = (
        UniqueConstraint("user_id", "summary_id", name="uq_user_summary"),
    )

    user = relationship("User", back_populates="sent_items")
    summary = relationship("ArticleSummary", back_populates="sent_items")
