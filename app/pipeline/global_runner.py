"""
Global Pipeline Runner
======================
Runs ONCE per schedule cycle. Fetches and processes all articles
from shared sources and stores them in the shared article pool.

Steps:
  1. Scrape all RSS + YouTube sources
  2. Process Anthropic HTML → Markdown
  3. Fetch YouTube transcripts
  4. Generate LLM summaries → article_summaries table (shared)
"""
import logging
import asyncio
from datetime import datetime

from app.runner import run_scrapers
from app.services.process_anthropic import process_anthropic_markdown
from app.services.process_youtube import process_youtube_transcripts
from app.services.process_digest import process_digests

logger = logging.getLogger(__name__)


def run_global_pipeline(hours: int = 24) -> dict:
    """
    Scrape → process → summarize all articles.
    Results saved to shared DB tables. No user-specific logic here.
    """
    start = datetime.now()
    logger.info("=" * 60)
    logger.info("[GLOBAL] Starting global pipeline")
    logger.info("=" * 60)

    results = {
        "start_time": start.isoformat(),
        "scraping": {},
        "processing": {},
        "summaries": {},
        "success": False,
    }

    try:
        # ── Step 1: Scrape all default sources ──────────────────
        logger.info("[GLOBAL 1/4] Scraping articles from all sources...")
        scraped = run_scrapers(hours=hours)
        results["scraping"] = {
            "youtube": len(scraped.get("youtube", [])),
            "openai": len(scraped.get("openai", [])),
            "anthropic": len(scraped.get("anthropic", [])),
        }
        logger.info(
            f"[GLOBAL] Scraped → YouTube: {results['scraping']['youtube']}, "
            f"OpenAI: {results['scraping']['openai']}, "
            f"Anthropic: {results['scraping']['anthropic']}"
        )

        # ── Step 2: Process Anthropic HTML → Markdown ───────────
        logger.info("[GLOBAL 2/4] Processing Anthropic markdown...")
        anthropic_result = process_anthropic_markdown()
        results["processing"]["anthropic"] = anthropic_result
        logger.info(
            f"[GLOBAL] Anthropic → {anthropic_result['processed']} processed, "
            f"{anthropic_result['failed']} failed"
        )

        # ── Step 3: Fetch YouTube transcripts ───────────────────
        logger.info("[GLOBAL 3/4] Fetching YouTube transcripts...")
        youtube_result = process_youtube_transcripts()
        results["processing"]["youtube"] = youtube_result
        logger.info(
            f"[GLOBAL] YouTube → {youtube_result['processed']} processed, "
            f"{youtube_result.get('unavailable', 0)} unavailable"
        )

        # ── Step 4: Generate article summaries (shared, once) ───
        logger.info("[GLOBAL 4/4] Generating article summaries (shared)...")
        summary_result = process_digests()
        results["summaries"] = summary_result
        logger.info(
            f"[GLOBAL] Summaries → {summary_result['processed']} new, "
            f"{summary_result['failed']} failed of {summary_result['total']} total"
        )

        results["success"] = True

    except Exception as e:
        logger.error(f"[GLOBAL] Pipeline failed: {e}", exc_info=True)
        results["error"] = str(e)

    duration = (datetime.now() - start).total_seconds()
    results["duration_seconds"] = duration
    logger.info(f"[GLOBAL] Finished in {duration:.1f}s — success={results['success']}")
    return results


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    run_global_pipeline(hours=180)

