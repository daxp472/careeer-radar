import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class JobCandidateSkillGap(Base):
    __tablename__ = "job_candidate_skill_gaps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("job_candidate_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)

    gap_type = Column(String(20), nullable=False)  # matched, weak, missing
    job_importance = Column(String(20), default="required", nullable=False)  # required, preferred, mentioned
    candidate_proficiency = Column(String(20), nullable=True)  # beginner, known, intermediate, advanced, expert
    priority_score = Column(Float, default=0.0, nullable=False)
    evidence = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("analysis_id", "skill_id", name="uq_job_candidate_analysis_skill"),
    )

    analysis = relationship("JobCandidateAnalysis", back_populates="gaps")
    skill = relationship("Skill")
