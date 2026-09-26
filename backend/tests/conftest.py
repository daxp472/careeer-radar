import pytest
from app.core.database import SessionLocal, Base, engine, ensure_db_schema_sync
from app.core.init_db import init_db
import app.models  # Ensure all models are imported into Base.metadata


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure database schema and canonical seed data exist before running tests."""
    Base.metadata.create_all(bind=engine)
    ensure_db_schema_sync()
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
