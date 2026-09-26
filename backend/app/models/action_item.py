import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("readiness_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=1, nullable=False)  # 1 = Highest priority
    estimated_effort_hours = Column(Integer, default=10)
    generated_by = Column(String(20), default="ai")  # ai, rule
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    analysis = relationship("ReadinessAnalysis", back_populates="action_items")
    skill = relationship("Skill", back_populates="action_items")
