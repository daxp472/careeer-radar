import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class MarketSkillStat(Base):
    __tablename__ = "market_skill_stats"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_id = Column(String(36), ForeignKey("market_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    jobs_with_skill = Column(Integer, default=0, nullable=False)
    total_mentions = Column(Integer, default=0, nullable=False)
    frequency_pct = Column(Float, default=0.0, nullable=False)  # e.g., 73.5%
    market_importance_score = Column(Float, default=0.0, nullable=False)

    __table_args__ = (
        UniqueConstraint("snapshot_id", "skill_id", name="uq_snapshot_skill"),
    )

    snapshot = relationship("MarketSnapshot", back_populates="skill_stats")
    skill = relationship("Skill", back_populates="market_stats")
