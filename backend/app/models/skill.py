import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    normalized_name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=True, default="General")
    aliases = Column(JSON, default=list, nullable=False)  # List of alias strings
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    candidate_skills = relationship("CandidateSkill", back_populates="skill", cascade="all, delete-orphan")
    job_skills = relationship("JobSkill", back_populates="skill", cascade="all, delete-orphan")
    market_stats = relationship("MarketSkillStat", back_populates="skill", cascade="all, delete-orphan")
    gaps = relationship("ReadinessGap", back_populates="skill", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="skill", cascade="all, delete-orphan")
