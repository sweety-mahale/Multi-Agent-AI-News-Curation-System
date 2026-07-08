import sys
from app.database.connection import get_database_info, engine
from sqlalchemy import text, inspect

if __name__ == "__main__":
    db_info = get_database_info()

    print("\n" + "=" * 60)
    print("Database Connection Check")
    print("=" * 60)
    print(f"Environment: {db_info['environment']}")
    print(f"Database URL: {db_info['url_masked']}")
    print(f"Host: {db_info['host']}")
    print("=" * 60 + "\n")

    EXPECTED_TABLES = [
        # Global shared tables
        "youtube_videos",
        "openai_articles",
        "anthropic_articles",
        "article_summaries",
        # Per-user tables
        "users",
        "user_profiles",
        "user_sources",
        "user_email_settings",
        "user_sent_items",
    ]

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Connection successful!")
            print(f"✓ PostgreSQL version: {version.split(',')[0]}\n")

            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()

            print("Table Check:")
            print("-" * 40)
            all_ok = True
            for table in EXPECTED_TABLES:
                if table in existing_tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  ✓ {table:<25} ({count} rows)")
                else:
                    print(f"  ✗ {table:<25} MISSING — run: uv run alembic upgrade head")
                    all_ok = False

            print()
            if all_ok:
                print("✓ All tables verified. Database is ready.")
            else:
                print("✗ Some tables are missing. Run migrations first.")
                sys.exit(1)

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)
