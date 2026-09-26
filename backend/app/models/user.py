import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="user", cascade="all, delete-orphan")
    searches = relationship("SearchRun", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("ReadinessAnalysis", back_populates="user", cascade="all, delete-orphan")
    watchlist_items = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    skill_progress = relationship("SkillProgressHistory", back_populates="user", cascade="all, delete-orphan")
    alert_settings = relationship("CandidateJobAlertSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    job_scans = relationship("CandidateJobScan", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
