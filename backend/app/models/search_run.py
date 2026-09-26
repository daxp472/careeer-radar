import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class SearchRun(Base):
    __tablename__ = "search_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    query = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    provider = Column(String(50), default="serpapi")
    provider_engine = Column(String(50), default="google_jobs")
    status = Column(String(50), default="queued", index=True)  # queued, searching, processing, completed, failed
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    result_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    user = relationship("User", back_populates="searches")
    role = relationship("Role", back_populates="searches")
    jobs = relationship("SearchRunJob", back_populates="search_run", cascade="all, delete-orphan")
    snapshots = relationship("MarketSnapshot", back_populates="search_run", cascade="all, delete-orphan")
