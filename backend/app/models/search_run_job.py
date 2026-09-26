import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class SearchRunJob(Base):
    __tablename__ = "search_run_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    search_run_id = Column(String(36), ForeignKey("search_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    rank = Column(Integer, default=0)
    relevance_score = Column(Float, default=1.0)

    __table_args__ = (
        UniqueConstraint("search_run_id", "job_id", name="uq_search_run_job"),
    )

    search_run = relationship("SearchRun", back_populates="jobs")
    job = relationship("Job", back_populates="search_runs")
