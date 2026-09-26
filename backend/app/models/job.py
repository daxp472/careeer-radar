import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider = Column(String(50), default="serpapi_google_jobs", nullable=False)
    provider_job_id = Column(String(255), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    normalized_title = Column(String(255), index=True, nullable=False)
    company_name = Column(String(255), index=True, nullable=False)
    location = Column(String(255), nullable=True)
    remote_type = Column(String(50), default="unknown")
    description = Column(Text, nullable=True)
    apply_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    first_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = Column(String(20), default="active", index=True, nullable=False)  # active, stale, expired, removed
    raw_payload = Column(JSON, default=dict, nullable=True)

    __table_args__ = (
        UniqueConstraint("provider", "provider_job_id", name="uq_provider_job_id"),
    )

    search_runs = relationship("SearchRunJob", back_populates="job", cascade="all, delete-orphan")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    watchlist_entries = relationship("Watchlist", back_populates="job", cascade="all, delete-orphan")
