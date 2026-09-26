import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    type = Column(String(50), default="weekly_job_digest", nullable=False)  # weekly_job_digest, new_job_match, reminder, job_update
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, default=dict, nullable=True)  # Metadata e.g. job_id, count, match_score

    is_read = Column(Boolean, default=False, index=True, nullable=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    user = relationship("User", back_populates="notifications")
