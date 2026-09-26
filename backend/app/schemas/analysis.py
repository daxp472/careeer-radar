from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.profile import CandidateSkillInput
from app.schemas.job import JobMatchSummary


class AnalyzeRequest(BaseModel):
    target_role: str
    location: Optional[str] = "India"
    remote_preference: Optional[str] = "flexible"
    skills: List[CandidateSkillInput]
    experience_years: Optional[int] = 0


class MarketSkillStatItem(BaseModel):
    skill_id: str
    name: str
    category: Optional[str]
    jobs_with_skill: int
    frequency_pct: float
    total_mentions: int
    importance_score: float

    model_config = ConfigDict(from_attributes=True)


class ReadinessGapItem(BaseModel):
    skill_id: str
    name: str
    category: Optional[str]
    gap_type: str  # matched, weak, missing
    market_frequency_pct: float
    importance_score: float
    candidate_proficiency: Optional[str]
    priority_score: float
    explanation: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ActionItemSchema(BaseModel):
    id: str
    skill_name: Optional[str]
    title: str
    description: str
    priority: int
    estimated_effort_hours: int
    generated_by: str

    model_config = ConfigDict(from_attributes=True)


class MarketRecommendationItem(BaseModel):
    skill_id: Optional[str] = None
    skill_name: str
    priority: int
    why_it_matters: str
    current_state: str
    recommended_next_step: str
    practical_action: str
    evidence: str
    market_frequency_pct: float
    recurring_jobs_count: int
    total_jobs_analyzed: int
    generated_by: str = "rule"

    model_config = ConfigDict(from_attributes=True)


class AnalysisResponse(BaseModel):
    id: str
    status: str
    target_role: str
    location: Optional[str]
    jobs_analyzed: int
    readiness_score: float  # Deterministic 0-100%
    summary: Optional[str]  # AI explanation based on verified evidence
    created_at: datetime
    
    market_skills: List[MarketSkillStatItem] = []
    gaps: List[ReadinessGapItem] = []
    matched_skills: List[ReadinessGapItem] = []
    weak_skills: List[ReadinessGapItem] = []
    missing_skills: List[ReadinessGapItem] = []
    action_items: List[ActionItemSchema] = []
    market_recommendations: List[MarketRecommendationItem] = []
    
    # Phase 2: Granular Job-Level Match Summaries
    job_matches: List[JobMatchSummary] = []

    model_config = ConfigDict(from_attributes=True)


class SkillChangeItem(BaseModel):
    skill_name: str
    category: Optional[str] = "General"
    from_proficiency: Optional[str] = None
    to_proficiency: str
    change_type: str  # acquired, improved, weakened, removed_gap, new_gap
    market_frequency_pct: Optional[float] = 0.0


class WhatChangedResponse(BaseModel):
    has_previous_analysis: bool
    current_analysis_id: str
    previous_analysis_id: Optional[str] = None
    current_created_at: datetime
    previous_created_at: Optional[datetime] = None
    
    current_readiness_score: float
    previous_readiness_score: Optional[float] = None
    readiness_score_change: float = 0.0
    
    current_jobs_count: int
    previous_jobs_count: Optional[int] = None
    
    newly_acquired_skills: List[SkillChangeItem] = []
    improved_proficiencies: List[SkillChangeItem] = []
    weakened_skills: List[SkillChangeItem] = []
    removed_gaps: List[SkillChangeItem] = []
    new_gaps: List[SkillChangeItem] = []
    
    jobs_above_threshold_change: int = 0
    market_priority_shifts: List[Dict[str, Any]] = []
    
    summary: str


class CandidateFeedbackSection(BaseModel):
    title: str
    badge: Optional[str] = None
    summary: str
    items: List[Dict[str, Any]] = []


class CandidateFeedbackReportResponse(BaseModel):
    analysis_id: str
    target_role: str
    location: str
    readiness_score: float
    alignment_tier: str  # Highly Ready, Strong Alignment, Building Foundation, Early Stage
    analyzed_at: datetime
    
    current_position: CandidateFeedbackSection
    strongest_areas: CandidateFeedbackSection
    biggest_gaps: CandidateFeedbackSection
    what_changed: WhatChangedResponse
    market_signals: CandidateFeedbackSection
    personalized_action_plan: List[MarketRecommendationItem] = []

