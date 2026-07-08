# Database Management

## Entity Relationship (ER) Diagram

The system uses a PostgreSQL database structured around global content collection (scraped items and shared summaries) and tenant-specific configuration (users, profiles, customized feeds, schedules, and delivery history).

```mermaid
erDiagram
    users {
        string id PK "UUID"
        string email UK "User's email"
        string hashed_password "BCrypt hashed"
        boolean is_active "Deactivation flag"
        datetime created_at
        datetime updated_at
    }
    user_profiles {
        string id PK "UUID"
        string user_id FK "users.id"
        string name "User display name"
        string title "Job title/role"
        string background "Professional background text"
        json interests "List of AI interest tags"
        json preferences "Preference key-value pairs"
        string expertise_level "Beginner | Intermediate | Expert"
        datetime created_at
        datetime updated_at
    }
    user_sources {
        string id PK "UUID"
        string user_id FK "users.id"
        string source_type "youtube | rss"
        string name "Source label"
        string url "Feed URL or Channel ID"
        boolean is_active
        datetime created_at
    }
    user_email_settings {
        string id PK "UUID"
        string user_id FK "users.id"
        string email_address "Delivery address"
        string frequency "daily | weekly"
        int delivery_hour "UTC hour (0-23)"
        string delivery_day "For weekly frequency (e.g. monday)"
        int top_n "Digest article count"
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    user_sent_items {
        string id PK "UUID"
        string user_id FK "users.id"
        string summary_id FK "article_summaries.id"
        int rank "Rank in digest email"
        float relevance_score "Similarity score (0.0-10.0)"
        datetime sent_at
    }
    article_summaries {
        string id PK "Format: type:article_id"
        string article_type "youtube | openai | anthropic"
        string article_id
        string url "Direct link to article"
        string title "LLM-generated title"
        string summary "LLM-generated summary"
        datetime created_at
    }
    youtube_videos {
        string video_id PK "YouTube Video ID"
        string title
        string url
        string channel_id
        datetime published_at
        string description
        string transcript "Scraped transcript text"
        datetime created_at
    }
    openai_articles {
        string guid PK "OpenAI post GUID"
        string title
        string url
        string description
        datetime published_at
        string category
        datetime created_at
    }
    anthropic_articles {
        string guid PK "Anthropic post GUID"
        string title
        string url
        string description
        datetime published_at
        string category
        string markdown "Cleaned web content"
        datetime created_at
    }

    users ||--|| user_profiles : "has profile"
    users ||--o{ user_sources : "configures sources"
    users ||--|| user_email_settings : "has email preferences"
    users ||--o{ user_sent_items : "received digests"
    article_summaries ||--o{ user_sent_items : "contains summary"
```

## Environment Configuration

The system supports two environments: **LOCAL** and **PRODUCTION**.

### Setting Environment

Set the `ENVIRONMENT` variable in your `.env` file:

```bash
# For local development
ENVIRONMENT=LOCAL

# For production (Render)
ENVIRONMENT=PRODUCTION
```

If not set, defaults to `LOCAL`.

### Database Connection

The system automatically detects the environment based on:
1. `ENVIRONMENT` variable
2. Database URL (if contains `render.com` or `amazonaws.com`, treated as PRODUCTION)

**Local Development:**
- Uses `POSTGRES_*` environment variables
- Defaults to `localhost:5432`

**Production (Render):**
- Uses `DATABASE_URL` (automatically provided by Render)
- No manual configuration needed

## Migration Scripts

### Check Database Connection

```bash
python app/database/check_connection.py
```

Shows:
- Current environment (LOCAL/PRODUCTION)
- Database connection status
- Table information
- Column existence

### Run Migration

```bash
# Local database
python app/database/migrate_add_sent_at.py

# Production database (requires confirmation)
ENVIRONMENT=PRODUCTION python app/database/migrate_add_sent_at.py
```

**Safety Features:**
- Shows environment and database info before running
- Requires explicit confirmation for PRODUCTION migrations
- Safe to run multiple times (uses `IF NOT EXISTS`)

## Switching Environments

### Local Development
```bash
# In .env file
ENVIRONMENT=LOCAL
DATABASE_URL=  # Leave empty or use local connection string
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_news_aggregator
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### Production (Render)
```bash
# In Render dashboard, set:
ENVIRONMENT=PRODUCTION
# DATABASE_URL is automatically set by Render
```

### Manual Production Migration

To run migrations on production database locally:

1. Get production `DATABASE_URL` from Render dashboard
2. Set environment variables:
```bash
export ENVIRONMENT=PRODUCTION
export DATABASE_URL=postgresql://user:pass@host:port/dbname
```
3. Run migration:
```bash
python app/database/migrate_add_sent_at.py
```
4. Confirm when prompted (type 'yes')

## Best Practices

1. **Always check connection first** before running migrations
2. **Use LOCAL for development** - safer and faster
3. **Double-check environment** before production migrations
4. **Keep .env file local** - never commit production credentials
5. **Use Render environment variables** for production deployments

