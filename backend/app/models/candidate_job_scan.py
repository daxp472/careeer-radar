import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class CandidateJobScan(Base):
    __tablename__ = "candidate_job_scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    jobs_checked = Column(Integer, default=0, nullable=False)
    jobs_matched = Column(Integer, default=0, nullable=False)
    jobs_above_threshold = Column(Integer, default=0, nullable=False)

    email_sent = Column(Boolean, default=False, nullable=False)
    status = Column(String(20), default="queued", nullable=False)  # queued, processing, completed, failed
    error_message = Column(Text, nullable=True)

    user = relationship("User", back_populates="job_scans")
