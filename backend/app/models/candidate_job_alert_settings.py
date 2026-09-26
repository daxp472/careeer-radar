import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class CandidateJobAlertSettings(Base):
    __tablename__ = "candidate_job_alert_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    enabled = Column(Boolean, default=True, nullable=False)
    frequency = Column(String(20), default="weekly", nullable=False)  # weekly, daily
    day_of_week = Column(String(20), default="monday", nullable=False)  # monday, tuesday, etc.
    time_of_day = Column(String(10), default="10:00", nullable=False)  # HH:MM format
    timezone = Column(String(50), default="Asia/Kolkata", nullable=False)
    minimum_match_score = Column(Float, default=80.0, nullable=False)  # e.g., 80%

    email_enabled = Column(Boolean, default=True, nullable=False)
    in_app_enabled = Column(Boolean, default=True, nullable=False)

    last_scan_at = Column(DateTime, nullable=True)
    next_scan_at = Column(DateTime, nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="alert_settings")
