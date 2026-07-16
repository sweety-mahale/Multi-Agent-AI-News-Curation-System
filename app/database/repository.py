from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import (
    YouTubeVideo, OpenAIArticle, AnthropicArticle,
    ArticleSummary, User, UserProfile, UserSource,
    UserEmailSettings, UserSentItem,
)
from .connection import get_session


class Repository:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()

    # ──────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────

    def _bulk_create_items(
        self,
        items: List[dict],
        model_class,
        id_field: str,
        id_attr: str,
    ) -> int:
        new_items = []
        for item in items:
            existing = (
                self.session.query(model_class)
                .filter_by(**{id_attr: item[id_field]})
                .first()
            )
            if not existing:
                new_items.append(model_class(**item))
        if new_items:
            self.session.add_all(new_items)
            self.session.commit()
        return len(new_items)

    # ──────────────────────────────────────────────────────────
    # GLOBAL: YouTube Videos
    # ──────────────────────────────────────────────────────────

    def bulk_create_youtube_videos(self, videos: List[dict]) -> int:
        formatted = [
            {
                "video_id": v["video_id"],
                "title": v["title"],
                "url": v["url"],
                "channel_id": v.get("channel_id", ""),
                "published_at": v["published_at"],
                "description": v.get("description", ""),
                "transcript": v.get("transcript"),
            }
            for v in videos
        ]
        return self._bulk_create_items(formatted, YouTubeVideo, "video_id", "video_id")

    def get_youtube_videos_without_transcript(
        self, limit: Optional[int] = None
    ) -> List[YouTubeVideo]:
        query = self.session.query(YouTubeVideo).filter(
            YouTubeVideo.transcript.is_(None)
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def update_youtube_video_transcript(self, video_id: str, transcript: str) -> bool:
        video = self.session.query(YouTubeVideo).filter_by(video_id=video_id).first()
        if video:
            video.transcript = transcript
            self.session.commit()
            return True
        return False

    # ──────────────────────────────────────────────────────────
    # GLOBAL: OpenAI Articles
    # ──────────────────────────────────────────────────────────

    def bulk_create_openai_articles(self, articles: List[dict]) -> int:
        formatted = [
            {
                "guid": a["guid"],
                "title": a["title"],
                "url": a["url"],
                "published_at": a["published_at"],
                "description": a.get("description", ""),
                "category": a.get("category"),
            }
            for a in articles
        ]
        return self._bulk_create_items(formatted, OpenAIArticle, "guid", "guid")

    # ──────────────────────────────────────────────────────────
    # GLOBAL: Anthropic Articles
    # ──────────────────────────────────────────────────────────

    def bulk_create_anthropic_articles(self, articles: List[dict]) -> int:
        formatted = [
            {
                "guid": a["guid"],
                "title": a["title"],
                "url": a["url"],
                "published_at": a["published_at"],
                "description": a.get("description", ""),
                "category": a.get("category"),
            }
            for a in articles
        ]
        return self._bulk_create_items(formatted, AnthropicArticle, "guid", "guid")

    def get_anthropic_articles_without_markdown(
        self, limit: Optional[int] = None
    ) -> List[AnthropicArticle]:
        query = self.session.query(AnthropicArticle).filter(
            AnthropicArticle.markdown.is_(None)
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def update_anthropic_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(AnthropicArticle).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            self.session.commit()
            return True
        return False

    # ──────────────────────────────────────────────────────────
    # GLOBAL: Article Summaries (replaces old Digest table)
    # Generated ONCE per article, shared across all users.
    # ──────────────────────────────────────────────────────────

    def get_articles_without_summary(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns all articles (YouTube/OpenAI/Anthropic) that do not yet
        have an entry in article_summaries. Used by the global summarizer.
        """
        articles = []
        existing_ids = {
            s.id for s in self.session.query(ArticleSummary.id).all()
        }

        # YouTube videos with transcript
        for video in (
            self.session.query(YouTubeVideo)
            .filter(
                YouTubeVideo.transcript.isnot(None),
                YouTubeVideo.transcript != "__UNAVAILABLE__",
            )
            .all()
        ):
            key = f"youtube:{video.video_id}"
            if key not in existing_ids:
                articles.append({
                    "type": "youtube",
                    "id": video.video_id,
                    "title": video.title,
                    "url": video.url,
                    "content": video.transcript or video.description or "",
                    "published_at": video.published_at,
                })

        # OpenAI articles
        for article in self.session.query(OpenAIArticle).all():
            key = f"openai:{article.guid}"
            if key not in existing_ids:
                articles.append({
                    "type": "openai",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.description or "",
                    "published_at": article.published_at,
                })

        # Anthropic articles with markdown
        for article in (
            self.session.query(AnthropicArticle)
            .filter(AnthropicArticle.markdown.isnot(None))
            .all()
        ):
            key = f"anthropic:{article.guid}"
            if key not in existing_ids:
                articles.append({
                    "type": "anthropic",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.markdown or article.description or "",
                    "published_at": article.published_at,
                })

        if limit:
            articles = articles[:limit]
        return articles

    def create_article_summary(
        self,
        article_type: str,
        article_id: str,
        url: str,
        title: str,
        summary: str,
        published_at: Optional[datetime] = None,
    ) -> Optional[ArticleSummary]:
        """Create a shared article summary. Idempotent — skips if already exists."""
        summary_id = f"{article_type}:{article_id}"
        if self.session.query(ArticleSummary).filter_by(id=summary_id).first():
            return None

        if published_at:
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            created_at = published_at
        else:
            created_at = datetime.now(timezone.utc)

        record = ArticleSummary(
            id=summary_id,
            article_type=article_type,
            article_id=article_id,
            url=url,
            title=title,
            summary=summary,
            created_at=created_at,
        )
        self.session.add(record)
        self.session.commit()
        return record

    def get_recent_article_summaries(
        self, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Returns all article summaries created within the given window.
        Used as input to the per-user CuratorAgent.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        summaries = (
            self.session.query(ArticleSummary)
            .filter(ArticleSummary.created_at >= cutoff)
            .order_by(ArticleSummary.created_at.desc())
            .all()
        )
        return [
            {
                "id": s.id,
                "article_type": s.article_type,
                "article_id": s.article_id,
                "url": s.url,
                "title": s.title,
                "summary": s.summary,
                "created_at": s.created_at,
            }
            for s in summaries
        ]

    # ──────────────────────────────────────────────────────────
    # PER-USER: User Accounts
    # ──────────────────────────────────────────────────────────

    def create_user(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter_by(email=email).first()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()

    def get_all_active_users(self) -> List[User]:
        return self.session.query(User).filter_by(is_active=True).all()

    def deactivate_user(self, user_id: str) -> bool:
        user = self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            self.session.commit()
            return True
        return False

    # ──────────────────────────────────────────────────────────
    # PER-USER: User Profiles
    # ──────────────────────────────────────────────────────────

    def create_user_profile(
        self,
        user_id: str,
        name: str,
        title: str = "",
        background: str = "",
        interests: Optional[list] = None,
        preferences: Optional[dict] = None,
        expertise_level: str = "Intermediate",
    ) -> UserProfile:
        profile = UserProfile(
            user_id=user_id,
            name=name,
            title=title,
            background=background,
            interests=interests or [],
            preferences=preferences or {},
            expertise_level=expertise_level,
        )
        self.session.add(profile)
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        return self.session.query(UserProfile).filter_by(user_id=user_id).first()

    def update_user_profile(self, user_id: str, **fields) -> Optional[UserProfile]:
        profile = self.get_user_profile(user_id)
        if not profile:
            return None
        for key, value in fields.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.updated_at = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(profile)
        return profile

    # ──────────────────────────────────────────────────────────
    # PER-USER: User Sources
    # ──────────────────────────────────────────────────────────

    def get_user_sources(self, user_id: str) -> List[UserSource]:
        return (
            self.session.query(UserSource)
            .filter_by(user_id=user_id, is_active=True)
            .all()
        )

    def create_user_source(
        self,
        user_id: str,
        source_type: str,
        name: str,
        url: str,
    ) -> UserSource:
        source = UserSource(
            user_id=user_id,
            source_type=source_type,
            name=name,
            url=url,
        )
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source

    def delete_user_source(self, source_id: str, user_id: str) -> bool:
        source = (
            self.session.query(UserSource)
            .filter_by(id=source_id, user_id=user_id)
            .first()
        )
        if source:
            source.is_active = False
            self.session.commit()
            return True
        return False

    # ──────────────────────────────────────────────────────────
    # PER-USER: Email Settings
    # ──────────────────────────────────────────────────────────

    def create_user_email_settings(
        self,
        user_id: str,
        email_address: str,
        frequency: str = "daily",
        delivery_hour: int = 8,
        delivery_day: Optional[str] = None,
        top_n: int = 10,
    ) -> UserEmailSettings:
        settings = UserEmailSettings(
            user_id=user_id,
            email_address=email_address,
            frequency=frequency,
            delivery_hour=delivery_hour,
            delivery_day=delivery_day,
            top_n=top_n,
        )
        self.session.add(settings)
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def get_user_email_settings(self, user_id: str) -> Optional[UserEmailSettings]:
        return (
            self.session.query(UserEmailSettings).filter_by(user_id=user_id).first()
        )

    def update_user_email_settings(
        self, user_id: str, **fields
    ) -> Optional[UserEmailSettings]:
        settings = self.get_user_email_settings(user_id)
        if not settings:
            return None
        for key, value in fields.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        settings.updated_at = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(settings)
        return settings

    # ──────────────────────────────────────────────────────────
    # PER-USER: Sent Items (replaces old sent_at on Digest)
    # ──────────────────────────────────────────────────────────

    def get_user_unread_summaries(
        self, user_id: str, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Returns article summaries from the last `hours` that have NOT yet
        been sent to this specific user. Used by the per-user curator.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)  # naive UTC to match stored created_at

        # IDs already sent to this user
        sent_ids = {
            row.summary_id
            for row in self.session.query(UserSentItem.summary_id)
            .filter_by(user_id=user_id)
            .all()
        }

        summaries = (
            self.session.query(ArticleSummary)
            .filter(ArticleSummary.created_at >= cutoff)
            .order_by(ArticleSummary.created_at.desc())
            .all()
        )

        return [
            {
                "id": s.id,
                "article_type": s.article_type,
                "article_id": s.article_id,
                "url": s.url,
                "title": s.title,
                "summary": s.summary,
                "created_at": s.created_at,
            }
            for s in summaries
            if s.id not in sent_ids
        ]

    def mark_summaries_as_sent(
        self,
        user_id: str,
        items: List[Dict[str, Any]],  # [{"summary_id", "rank", "relevance_score"}]
    ) -> int:
        """Record which summaries were sent to a user and their ranking."""
        now = datetime.now(timezone.utc)
        created = 0
        for item in items:
            existing = (
                self.session.query(UserSentItem)
                .filter_by(user_id=user_id, summary_id=item["summary_id"])
                .first()
            )
            if not existing:
                record = UserSentItem(
                    user_id=user_id,
                    summary_id=item["summary_id"],
                    rank=item.get("rank"),
                    relevance_score=item.get("relevance_score"),
                    sent_at=now,
                )
                self.session.add(record)
                created += 1
        self.session.commit()
        return created

    def get_user_sent_history(
        self, user_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Returns the most recent digests sent to a user (for the dashboard)."""
        items = (
            self.session.query(UserSentItem)
            .filter_by(user_id=user_id)
            .order_by(UserSentItem.sent_at.desc())
            .limit(limit)
            .all()
        )
        result = []
        for item in items:
            summary = item.summary
            if summary:
                result.append({
                    "summary_id": item.summary_id,
                    "rank": item.rank,
                    "relevance_score": item.relevance_score,
                    "sent_at": item.sent_at,
                    "title": summary.title,
                    "summary": summary.summary,
                    "url": summary.url,
                    "article_type": summary.article_type,
                })
        return result
