import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON
from app.core.database import Base


class JobIngestionReport(Base):
    __tablename__ = "job_ingestion_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    roles_queried = Column(Integer, default=0)
    locations_queried = Column(Integer, default=0)
    total_jobs_fetched = Column(Integer, default=0)
    new_jobs_inserted = Column(Integer, default=0)
    existing_jobs_updated = Column(Integer, default=0)
    jobs_marked_stale = Column(Integer, default=0)

    status = Column(String(20), default="processing", nullable=False)  # processing, completed, failed
    metadata_payload = Column(JSON, default=dict, nullable=True)
