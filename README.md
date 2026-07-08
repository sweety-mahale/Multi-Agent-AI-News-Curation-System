# Multi-Agent AI News Curation System

An intelligent news aggregation system that scrapes AI-related content from multiple sources (YouTube channels, RSS feeds), processes them with LLM-powered summarization, curates personalized digests based on user preferences, and delivers daily email summaries.

## Overview

This project aggregates AI news from multiple sources:
- **YouTube Channels**: Scrapes videos and transcripts from configured channels
- **RSS Feeds**: Monitors OpenAI and Anthropic blog posts
- **Processing**: Converts content to markdown, generates summaries, and creates digests
- **Multi-Tenant Curation**: Ranks articles by relevance to each user's unique profile using Gemini (`gemini-2.5-flash`)
- **Delivery & Dashboard**: Delivers personalized email digests and displays history in an interactive React.js web application


## Architecture

```mermaid
graph LR
    A[Sources<br/>YouTube<br/>RSS Feeds] --> B[Scrapers<br/>BaseScraper<br/>Registry Pattern]
    B --> C[(Database<br/>PostgreSQL)]
    C --> D[Processors<br/>Markdown<br/>Transcripts<br/>Digests]
    D --> C
    C --> E[Curator<br/>LLM Ranking]
    E --> F[Email<br/>Personalized Digest]
    F --> G[Delivery<br/>Gmail SMTP]
    
    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#e8f5e9,stroke:#4caf50,stroke-width:3px
    style D fill:#fff4e1
    style E fill:#f3e5f5
    style F fill:#f3e5f5
    style G fill:#ffe1f5
```

## How It Works

### Global vs. Per-User Pipeline Flow

To support multiple users efficiently without duplicate LLM API calls, the system divides processing into two distinct phases:

1.  **Global Scrape & Summarize (Once per cycle):**
    *   **Scraping:** (`app/runner.py`) fetches raw articles/videos from configured sources.
    *   **Processing:** (`app/services/process_anthropic.py` & `process_youtube.py`) prepares transcripts and clean markdown.
    *   **Shared Summarization:** (`app/services/process_digest.py`) calls `DigestAgent` (Gemini) to generate clean summaries, storing them in the shared `article_summaries` table.

2.  **Per-User Curation & Delivery (Triggered per user schedule):**
    *   **Filtering:** Looks up summaries created in the active window (e.g. 24 hours) that have not been sent to this user yet.
    *   **Ranking:** (`CuratorAgent` / Gemini) ranks and scores these summaries based on the user's specific profile (interests, background, and expertise level).
    *   **Email Generation:** (`EmailAgent` / Gemini) reviews the top N matched articles and writes a personalized introduction newsletter greeting.
    *   **SMTP Delivery:** Sends the HTML email and records the sent history in `user_sent_items` so the dashboard feed is updated.

### Persistent Scheduler

A persistent `APScheduler` backed by the PostgreSQL database runs continuously inside the FastAPI application process:
-   **Global Job:** Automatically runs at 5 AM UTC daily to crawl and summarize the web.
-   **User Jobs:** Dynamically scheduled or updated based on each user's unique delivery configuration (daily/weekly, custom hour). Job schedules persist across server restarts.


## Project Structure

```
app/
├── agent/              # LLM agents for processing (Gemini GenAI SDK)
│   ├── base.py         # Base agent class
│   ├── curator_agent.py# User alignment/ranking agent
│   ├── digest_agent.py # Article summarization agent
│   └── email_agent.py  # Personal newsletter agent
├── api/                # FastAPI backend API
│   ├── main.py         # FastAPI main script & lifespans
│   ├── dependencies.py # JWT Auth & DB session providers
│   ├── schemas/        # Shared Pydantic data schemas
│   └── routers/        # API routers (auth, users, sources, digests, pipeline)
├── core/               # Security and token utilities
├── database/           # Database layer
│   ├── models.py       # SQLAlchemy models (9 tables)
│   ├── repository.py   # Data access layer
│   └── connection.py   # DB connection & environment
├── pipeline/           # Sequential runner workflows
│   ├── global_runner.py# Crawler & global summarizer script
│   ├── user_runner.py  # Personal curation & delivery script
│   └── scheduler.py    # Persistent task scheduler
├── scrapers/           # Content scrapers (YouTube/RSS)
├── services/           # Processing services
├── daily_runner.py     # Old main orchestrator (legacy)
└── runner.py           # Scraper registry & execution
frontend/               # React.js Vite application
```

## Adding New Scrapers

### RSS Feed Scraper (Easiest)

Create a new file in `app/scrapers/`:

```python
from typing import List
from .base import BaseScraper, Article

class MyArticle(Article):
    pass

class MyScraper(BaseScraper):
    @property
    def rss_urls(self) -> List[str]:
        return ["https://example.com/feed.xml"]

    def get_articles(self, hours: int = 24) -> List[MyArticle]:
        return [MyArticle(**a.model_dump()) for a in super().get_articles(hours)]
```

Then register it in `app/runner.py`:

```python
from .scrapers.my_scraper import MyScraper

def _save_my_articles(scraper, repo, hours):
    return _save_rss_articles(scraper, repo, hours, repo.bulk_create_my_articles)

SCRAPER_REGISTRY = [
    # ... existing scrapers
    ("my_source", MyScraper(), _save_my_articles),
]
```

### Custom Scraper

For non-RSS sources, inherit from the base pattern:

```python
class CustomScraper:
    def get_articles(self, hours: int = 24) -> List[Article]:
        # Your custom scraping logic
        pass
```

## Setup

### Prerequisites

- Python 3.12+
- Node.js (for React frontend)
- PostgreSQL database
- Gemini API key
- Gmail app password (for email sending)
- Webshare proxy credentials (optional, for YouTube transcript fetching)

### Installation

1. Clone the repository
2. Install Python dependencies:
   ```bash
   uv sync
   ```

3. Configure environment variables (copy `app/example.env` to `.env`):
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   MY_EMAIL=your_email@gmail.com
   APP_PASSWORD=your_gmail_app_password
   DATABASE_URL=postgresql://user:pass@host:port/db
   JWT_SECRET_KEY=generate_a_random_jwt_secret_key
   ```
   
   **Note**: Webshare proxy configuration is optional. If not provided, YouTube transcript fetching will work without a proxy but may be rate-limited.

4. Run migrations to initialize the 9-table schema:
   ```bash
   uv run alembic upgrade head
   ```
   
   Or check database connection and table counts:
   ```bash
   uv run python -m app.database.check_connection
   ```

5. Configure YouTube channels in `app/config.py`

6. Initialize custom sources and profile settings via the React Web UI dashboard once registered.


### Running

#### 1. Start the Backend Server (FastAPI)
Run the following in the project root:
```bash
uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```
-   Interactive API docs: `http://localhost:8000/docs`
-   Health checks: `http://localhost:8000/health`

#### 2. Start the Frontend Dashboard (React/Vite)
Navigate to the `frontend` directory, install Node packages, and run the developer server:
```bash
cd frontend
npm install
npm run dev
```
-   Web Dashboard: `http://localhost:5173`

#### 3. Trigger Crawling manually (Standalone)
You can run the global scraping and summarization script standalone using:
```bash
uv run python -m app.pipeline.global_runner
```

## Deployment

### Render.com

The project is configured for deployment on Render.com:

1. **Database**: PostgreSQL service (auto-configured)
2. **Cron Job**: Scheduled daily execution via `render.yaml`
3. **Environment**: Automatically detected as PRODUCTION when `DATABASE_URL` contains "render.com" (no manual setting needed)

See `RENDER_SETUP.md` for detailed deployment instructions.

### Docker

Build and run:
```bash
docker build -t ai-news-aggregator .
docker run --env-file .env ai-news-aggregator
```

## Key Features

- **Multi-Tenant SaaS Support**: Clean user registration, profile configuration, and individual SMTP email settings.
- **Sequential Multi-Agent Workflows**: Employs three specialized agents (`DigestAgent`, `CuratorAgent`, and `EmailAgent`) using Gemini.
- **Visual Web UI**: Premium obsidian-and-amber React dashboard for tracking sources and read digest logs.
- **Persistent Delivery Scheduling**: Dynamic user schedules backed by database-persisted APScheduler jobs.
- **Modular Architecture**: Base classes make it easy to extend scrapers and processors.
- **Scraper Registry**: Add new sources with minimal code.
- **Duplicate Prevention**: Tracks individual user delivery logs.

## Technology Stack

- **Python 3.12+**: Core language
- **FastAPI / Uvicorn**: Backend Web API framework
- **React.js / Vite**: Frontend Single Page Application
- **PostgreSQL / SQLAlchemy**: Database storage and ORM layer
- **Alembic**: Database migrations management
- **Google GenAI SDK**: Gemini-powered summaries and curation agents
- **feedparser**: RSS parsing
- **youtube-transcript-api**: Video transcripts
- **UV**: Python package management

## License

MIT

