import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    mention_count = Column(Integer, default=1)
    importance = Column(String(20), default="required", nullable=False)  # required, preferred, mentioned
    extraction_method = Column(String(20), default="rule", nullable=False)  # rule, nlp, llm, manual
    evidence = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),
    )

    job = relationship("Job", back_populates="skills")
    skill = relationship("Skill", back_populates="job_skills")
