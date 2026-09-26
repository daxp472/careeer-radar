import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    search_run_id = Column(String(36), ForeignKey("search_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True, index=True)
    location = Column(String(255), nullable=True)
    jobs_analyzed = Column(Integer, default=0, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    window_started_at = Column(DateTime, nullable=True)
    window_ended_at = Column(DateTime, nullable=True)

    search_run = relationship("SearchRun", back_populates="snapshots")
    role = relationship("Role", back_populates="snapshots")
    skill_stats = relationship("MarketSkillStat", back_populates="snapshot", cascade="all, delete-orphan")
    analyses = relationship("ReadinessAnalysis", back_populates="snapshot", cascade="all, delete-orphan")
