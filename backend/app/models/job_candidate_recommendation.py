import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class JobCandidateRecommendation(Base):
    __tablename__ = "job_candidate_recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("job_candidate_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)

    priority = Column(Integer, default=1, nullable=False)
    why_it_matters = Column(Text, nullable=False)
    current_state = Column(Text, nullable=False)
    recommended_next_step = Column(Text, nullable=False)
    practical_action = Column(Text, nullable=False)
    evidence = Column(Text, nullable=False)
    generated_by = Column(String(20), default="rule", nullable=False)  # rule, ai
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    analysis = relationship("JobCandidateAnalysis", back_populates="recommendations")
    skill = relationship("Skill")
