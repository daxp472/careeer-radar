import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ReadinessAnalysis(Base):
    __tablename__ = "readiness_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_id = Column(String(36), ForeignKey("market_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    readiness_score = Column(Float, default=0.0, nullable=False)  # 0 to 100 deterministic
    status = Column(String(50), default="completed", nullable=False)  # queued, analyzing, completed, failed
    summary = Column(Text, nullable=True)  # LLM generated evidence-backed explanation
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="analyses")
    snapshot = relationship("MarketSnapshot", back_populates="analyses")
    gaps = relationship("ReadinessGap", back_populates="analysis", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="analysis", cascade="all, delete-orphan")
