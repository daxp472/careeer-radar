import uuid
from sqlalchemy import Column, String, Float, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class ReadinessGap(Base):
    __tablename__ = "readiness_gaps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("readiness_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    gap_type = Column(String(20), nullable=False)  # matched, weak, missing
    market_frequency_pct = Column(Float, default=0.0, nullable=False)
    importance_score = Column(Float, default=0.0, nullable=False)
    candidate_proficiency = Column(String(20), nullable=True)  # beginner, known, intermediate, advanced, expert, or None
    priority_score = Column(Float, default=0.0, nullable=False)
    explanation = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("analysis_id", "skill_id", name="uq_analysis_skill_gap"),
    )

    analysis = relationship("ReadinessAnalysis", back_populates="gaps")
    skill = relationship("Skill", back_populates="gaps")
