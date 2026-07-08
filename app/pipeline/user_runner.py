"""
Per-User Pipeline Runner
========================
Runs separately for EACH user. Reads from the shared article_summaries
pool, ranks articles using the user's personal profile, generates a
personalized email introduction, and sends the digest.

Steps:
  1. Load user's profile + email settings from DB
  2. Fetch article summaries not yet seen by this user
  3. Run CuratorAgent (GPT-4.1) → ranked list
  4. Run EmailAgent (GPT-4o-mini) → personalized intro
  5. Send email via SMTP
  6. Record sent items in user_sent_items
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from app.database.repository import Repository
from app.agent.curator_agent import CuratorAgent
from app.agent.email_agent import EmailAgent, RankedArticleDetail
from app.services.email import send_email, digest_to_html

logger = logging.getLogger(__name__)


def _build_user_profile_dict(profile, email_settings) -> dict:
    """Convert DB UserProfile + UserEmailSettings into the dict format agents expect."""
    return {
        "name": profile.name,
        "title": profile.title or "",
        "background": profile.background or "",
        "interests": profile.interests or [],
        "preferences": profile.preferences or {},
        "expertise_level": profile.expertise_level or "Intermediate",
        "email": email_settings.email_address if email_settings else "",
        "top_n": email_settings.top_n if email_settings else 10,
    }


def run_user_pipeline(user_id: str, hours: int = 24) -> dict:
    """
    Run the full curation + email pipeline for a single user.
    Reads from the shared article_summaries pool; sends to user only.
    """
    start = datetime.now()
    results = {
        "user_id": user_id,
        "start_time": start.isoformat(),
        "success": False,
        "articles_sent": 0,
    }

    repo = Repository()

    try:
        # ── Step 1: Load user data ───────────────────────────────
        user = repo.get_user_by_id(user_id)
        if not user or not user.is_active:
            logger.warning(f"[USER {user_id}] User not found or inactive. Skipping.")
            results["skipped"] = True
            results["reason"] = "User not found or inactive"
            return results

        profile = repo.get_user_profile(user_id)
        email_settings = repo.get_user_email_settings(user_id)

        if not profile:
            logger.warning(f"[USER {user_id}] No profile found. Skipping.")
            results["skipped"] = True
            results["reason"] = "No profile configured"
            return results

        if not email_settings or not email_settings.is_active:
            logger.warning(f"[USER {user_id}] Email disabled or not configured. Skipping.")
            results["skipped"] = True
            results["reason"] = "Email not configured or disabled"
            return results

        top_n = email_settings.top_n
        user_email = email_settings.email_address
        user_profile_dict = _build_user_profile_dict(profile, email_settings)

        logger.info(f"[USER {profile.name}] Starting curation for {user_email}")

        # ── Step 2: Fetch unread summaries for this user ─────────
        unread = repo.get_user_unread_summaries(user_id, hours=hours)
        if not unread:
            logger.info(f"[USER {profile.name}] No new articles to send. Skipping.")
            results["skipped"] = True
            results["reason"] = "No new articles available"
            results["success"] = True
            return results

        logger.info(f"[USER {profile.name}] Found {len(unread)} unread articles to rank")

        # ── Step 3: Rank articles with CuratorAgent (GPT-4.1) ────
        # Format summaries for the curator (uses 'id' key)
        curator_input = [
            {
                "id": s["id"],
                "title": s["title"],
                "summary": s["summary"],
                "article_type": s["article_type"],
                "url": s["url"],
            }
            for s in unread
        ]

        curator = CuratorAgent(user_profile_dict)
        ranked_articles = curator.rank_digests(curator_input)

        if not ranked_articles:
            logger.error(f"[USER {profile.name}] CuratorAgent returned no ranked articles.")
            results["error"] = "CuratorAgent failed to rank articles"
            return results

        # Sort by rank and limit to top_n
        ranked_articles.sort(key=lambda a: a.rank)
        top_articles = ranked_articles[:top_n]

        # Build summary lookup for quick access
        summary_map = {s["id"]: s for s in unread}

        # ── Step 4: Build EmailAgent input + generate intro ───────
        email_agent = EmailAgent(user_profile_dict)
        article_details = [
            RankedArticleDetail(
                digest_id=a.digest_id,
                rank=a.rank,
                relevance_score=a.relevance_score,
                reasoning=a.reasoning,
                title=summary_map.get(a.digest_id, {}).get("title", ""),
                summary=summary_map.get(a.digest_id, {}).get("summary", ""),
                url=summary_map.get(a.digest_id, {}).get("url", ""),
                article_type=summary_map.get(a.digest_id, {}).get("article_type", ""),
            )
            for a in top_articles
            if a.digest_id in summary_map
        ]

        email_digest = email_agent.create_email_digest_response(
            ranked_articles=article_details,
            total_ranked=len(ranked_articles),
            limit=top_n,
        )

        # ── Step 5: Send email via SMTP ───────────────────────────
        markdown_content = email_digest.to_markdown()
        html_content = digest_to_html(email_digest)
        subject = (
            f"Your AI News Digest — {datetime.now().strftime('%B %d, %Y')}"
        )

        send_email(
            subject=subject,
            body_text=markdown_content,
            body_html=html_content,
            recipients=[user_email],
        )
        logger.info(f"[USER {profile.name}] Email sent to {user_email} with {len(article_details)} articles")

        # ── Step 6: Record what was sent ──────────────────────────
        sent_items = [
            {
                "summary_id": a.digest_id,
                "rank": a.rank,
                "relevance_score": a.relevance_score,
            }
            for a in top_articles
            if a.digest_id in summary_map
        ]
        marked = repo.mark_summaries_as_sent(user_id, sent_items)
        logger.info(f"[USER {profile.name}] Recorded {marked} sent items")

        results["success"] = True
        results["articles_sent"] = len(article_details)
        results["subject"] = subject

    except Exception as e:
        logger.error(f"[USER {user_id}] Pipeline failed: {e}", exc_info=True)
        results["error"] = str(e)
    finally:
        repo.session.close()

    duration = (datetime.now() - start).total_seconds()
    results["duration_seconds"] = duration
    return results


def run_all_users_pipeline(hours: int = 24) -> list:
    """
    Run the per-user curation pipeline for ALL active users.
    Users are processed SEQUENTIALLY with a 1-second delay between each
    to avoid hitting OpenAI rate limits.
    """
    repo = Repository()
    users = repo.get_all_active_users()
    repo.session.close()

    logger.info(f"[PIPELINE] Starting per-user pipeline for {len(users)} users")

    all_results = []
    for i, user in enumerate(users):
        logger.info(f"[PIPELINE] Processing user {i+1}/{len(users)}: {user.email}")
        result = run_user_pipeline(user.id, hours=hours)
        all_results.append(result)

        # Rate limit: 1-second gap between users to respect OpenAI RPM limits
        if i < len(users) - 1:
            import time
            time.sleep(1)

    succeeded = sum(1 for r in all_results if r.get("success"))
    skipped = sum(1 for r in all_results if r.get("skipped"))
    failed = sum(1 for r in all_results if r.get("error"))

    logger.info(
        f"[PIPELINE] Completed: {succeeded} sent, {skipped} skipped, {failed} failed"
    )
    return all_results
