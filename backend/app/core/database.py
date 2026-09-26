import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from app.core.logging import logger

db_url = settings.DATABASE_URL

# Support graceful fallback to SQLite if PostgreSQL fails to connect during local dev
try:
    if db_url.startswith("postgresql"):
        # Test connection or configure pool
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        # Verify connectivity
        with engine.connect() as conn:
            logger.info("Successfully connected to PostgreSQL database.")
    else:
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
except Exception as e:
    logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite database for seamless development.")
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "careerradar.db")
    engine = create_engine(f"sqlite:///{sqlite_path}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_db_schema_sync():
    """
    Ensure newly added columns exist in tables during local SQLite dev.
    """
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Check jobs table columns
            if engine.url.drivername.startswith("sqlite"):
                columns_res = conn.execute(text("PRAGMA table_info(jobs)"))
                existing_cols = [row[1] for row in columns_res.fetchall()]
                if existing_cols:
                    if "status" not in existing_cols:
                        conn.execute(text("ALTER TABLE jobs ADD COLUMN status VARCHAR DEFAULT 'active'"))
                    if "updated_at" not in existing_cols:
                        conn.execute(text("ALTER TABLE jobs ADD COLUMN updated_at DATETIME"))
                    if "first_seen_at" not in existing_cols:
                        conn.execute(text("ALTER TABLE jobs ADD COLUMN first_seen_at DATETIME"))
                    if "last_seen_at" not in existing_cols:
                        conn.execute(text("ALTER TABLE jobs ADD COLUMN last_seen_at DATETIME"))
                    conn.commit()
    except Exception as e:
        logger.debug(f"Schema sync notice: {e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

