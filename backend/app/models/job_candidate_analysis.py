import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class JobCandidateAnalysis(Base):
    __tablename__ = "job_candidate_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    readiness_analysis_id = Column(String(36), ForeignKey("readiness_analyses.id", ondelete="CASCADE"), nullable=True, index=True)

    match_score = Column(Float, default=0.0, nullable=False)  # 0 to 100% deterministic
    required_match_score = Column(Float, default=0.0, nullable=False)
    preferred_match_score = Column(Float, default=0.0, nullable=False)

    total_required_skills = Column(Integer, default=0, nullable=False)
    matched_required_skills = Column(Integer, default=0, nullable=False)
    missing_required_skills = Column(Integer, default=0, nullable=False)
    weak_required_skills = Column(Integer, default=0, nullable=False)

    total_preferred_skills = Column(Integer, default=0, nullable=False)
    matched_preferred_skills = Column(Integer, default=0, nullable=False)
    missing_preferred_skills = Column(Integer, default=0, nullable=False)
    weak_preferred_skills = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    job = relationship("Job")
    user = relationship("User")
    readiness_analysis = relationship("ReadinessAnalysis")
    gaps = relationship("JobCandidateSkillGap", back_populates="analysis", cascade="all, delete-orphan")
    recommendations = relationship("JobCandidateRecommendation", back_populates="analysis", cascade="all, delete-orphan")
