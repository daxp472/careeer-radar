import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class SkillProgressHistory(Base):
    __tablename__ = "skill_progress_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    from_proficiency = Column(String(20), nullable=True)  # None/missing, beginner, known, intermediate, advanced, expert
    to_proficiency = Column(String(20), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="skill_progress")
    skill = relationship("Skill")
