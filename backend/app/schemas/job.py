from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class JobSkillItem(BaseModel):
    skill_id: str
    name: str
    category: Optional[str] = "General"
    importance: str = "required"  # required, preferred, mentioned
    mention_count: int = 1
    evidence: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class JobCandidateSkillGapItem(BaseModel):
    id: Optional[str] = None
    skill_id: str
    name: str
    category: Optional[str] = "General"
    gap_type: str  # matched, weak, missing
    job_importance: str  # required, preferred, mentioned
    candidate_proficiency: Optional[str] = None
    priority_score: float
    evidence: str
    market_frequency_pct: Optional[float] = 0.0

    model_config = ConfigDict(from_attributes=True)


class JobCandidateRecommendationItem(BaseModel):
    id: Optional[str] = None
    skill_id: Optional[str] = None
    skill_name: Optional[str] = None
    priority: int
    why_it_matters: str
    current_state: str
    recommended_next_step: str
    practical_action: str
    evidence: str
    generated_by: str = "rule"

    model_config = ConfigDict(from_attributes=True)


class JobMatchSummary(BaseModel):
    job_id: str
    title: str
    company_name: str
    location: Optional[str] = None
    apply_url: Optional[str] = None
    posted_at: Optional[datetime] = None

    match_score: float  # 0 to 100%
    required_match_score: float
    preferred_match_score: float

    total_required_skills: int
    matched_required_skills: int
    missing_required_skills: int
    weak_required_skills: int

    total_preferred_skills: int
    matched_preferred_skills: int
    missing_preferred_skills: int
    weak_preferred_skills: int

    matched_skills: List[str] = []
    missing_required: List[str] = []
    missing_preferred: List[str] = []
    weak_skills: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class JobDetailedAnalysisResponse(BaseModel):
    job_id: str
    title: str
    company_name: str
    location: Optional[str] = None
    remote_type: Optional[str] = "unknown"
    description: Optional[str] = None
    apply_url: Optional[str] = None
    posted_at: Optional[datetime] = None

    match_score: float
    required_match_score: float
    preferred_match_score: float

    total_skills_count: int
    total_required_skills: int
    matched_required_skills: int
    missing_required_skills: int
    weak_required_skills: int

    total_preferred_skills: int
    matched_preferred_skills: int
    missing_preferred_skills: int
    weak_preferred_skills: int

    skills: List[JobSkillItem] = []
    gaps: List[JobCandidateSkillGapItem] = []
    matched_skills: List[JobCandidateSkillGapItem] = []
    missing_required_gaps: List[JobCandidateSkillGapItem] = []
    missing_preferred_gaps: List[JobCandidateSkillGapItem] = []
    weak_gaps: List[JobCandidateSkillGapItem] = []

    recommendations: List[JobCandidateRecommendationItem] = []

    model_config = ConfigDict(from_attributes=True)


class DatabaseJobItem(BaseModel):
    id: str
    title: str
    company_name: str
    location: Optional[str] = None
    remote_type: Optional[str] = "unknown"
    description: Optional[str] = None
    apply_url: Optional[str] = None
    status: str = "active"
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    skills: List[JobSkillItem] = []
    match_score: Optional[float] = None
    missing_skills: List[str] = []
    matched_skills: List[str] = []
    is_saved: bool = False

    model_config = ConfigDict(from_attributes=True)


class DatabaseJobSearchResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    jobs: List[DatabaseJobItem] = []
    applied_filters: Dict[str, Any] = {}
    database_last_refreshed_at: Optional[datetime] = None


class AdminRefreshResponse(BaseModel):
    status: str
    message: str
    report_id: Optional[str] = None
    total_found: int = 0
    total_inserted: int = 0
    total_updated: int = 0
    total_stale: int = 0
    errors_count: int = 0


class AdminStatusResponse(BaseModel):
    total_active_jobs: int
    total_stale_jobs: int
    total_expired_jobs: int
    total_jobs: int
    last_refresh_at: Optional[datetime] = None
    recent_reports: List[Dict[str, Any]] = []

