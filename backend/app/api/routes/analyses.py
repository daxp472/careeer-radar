from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_optional_current_user, get_current_user
from app.models import (
    User, ReadinessAnalysis, MarketSnapshot, MarketSkillStat,
    ReadinessGap, ActionItem, SearchRunJob, Job, JobSkill, Skill,
    JobCandidateAnalysis, JobCandidateSkillGap, JobCandidateRecommendation
)
from app.schemas.analysis import (
    AnalyzeRequest, AnalysisResponse, MarketSkillStatItem,
    ReadinessGapItem, ActionItemSchema, MarketRecommendationItem,
    WhatChangedResponse, CandidateFeedbackReportResponse
)
from app.schemas.job import JobMatchSummary
from app.services.market_analysis_service import market_analysis_service
from app.services.recommendation_service import recommendation_service
from app.services.progress_intelligence_service import progress_intelligence_service

router = APIRouter(prefix="/analyses", tags=["Market Readiness Analyses"])


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    req: AnalyzeRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger end-to-end live market analysis:
    Live Search -> Skill Extraction -> Frequency Aggregation -> Deterministic Readiness & Job-Level Gap Analyses -> Action Plans
    """
    skills_data = [s.model_dump() for s in req.skills]
    user_id = current_user.id if current_user else None

    analysis = await market_analysis_service.run_market_analysis(
        db=db,
        user_id=user_id,
        target_role=req.target_role,
        location=req.location or "India",
        skills_input=skills_data,
        experience_years=req.experience_years or 0
    )

    return get_analysis_by_id(analysis_id=analysis.id, db=db)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis_by_id(analysis_id: str, db: Session = Depends(get_db)):
    analysis = db.query(ReadinessAnalysis).filter(ReadinessAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis report not found.")

    snapshot = analysis.snapshot
    role_name = snapshot.role.name if snapshot and snapshot.role else "Developer"
    location = snapshot.location if snapshot else "Global"
    jobs_analyzed = snapshot.jobs_analyzed if snapshot else 0

    # Market Stats
    market_stats_records = db.query(MarketSkillStat).filter(MarketSkillStat.snapshot_id == snapshot.id).all() if snapshot else []
    market_skills = []
    for ms in market_stats_records:
        sk = ms.skill
        market_skills.append(MarketSkillStatItem(
            skill_id=ms.skill_id,
            name=sk.name if sk else "Skill",
            category=sk.category if sk else "General",
            jobs_with_skill=ms.jobs_with_skill,
            frequency_pct=ms.frequency_pct,
            total_mentions=ms.total_mentions,
            importance_score=ms.market_importance_score
        ))
    market_skills.sort(key=lambda x: x.frequency_pct, reverse=True)

    # Gaps
    gaps_records = db.query(ReadinessGap).filter(ReadinessGap.analysis_id == analysis.id).all()
    all_gaps = []
    matched_skills = []
    weak_skills = []
    missing_skills = []

    for g in gaps_records:
        sk = g.skill
        item = ReadinessGapItem(
            skill_id=g.skill_id,
            name=sk.name if sk else "Skill",
            category=sk.category if sk else "General",
            gap_type=g.gap_type,
            market_frequency_pct=g.market_frequency_pct,
            importance_score=g.importance_score,
            candidate_proficiency=g.candidate_proficiency,
            priority_score=g.priority_score,
            explanation=g.explanation
        )
        all_gaps.append(item)
        if g.gap_type == "matched":
            matched_skills.append(item)
        elif g.gap_type == "weak":
            weak_skills.append(item)
        else:
            missing_skills.append(item)

    all_gaps.sort(key=lambda x: x.priority_score, reverse=True)
    missing_skills.sort(key=lambda x: x.priority_score, reverse=True)
    weak_skills.sort(key=lambda x: x.priority_score, reverse=True)
    matched_skills.sort(key=lambda x: x.market_frequency_pct, reverse=True)

    # Action items
    actions_records = db.query(ActionItem).filter(ActionItem.analysis_id == analysis.id).order_by(ActionItem.priority).all()
    action_items = [
        ActionItemSchema(
            id=a.id,
            skill_name=a.skill.name if a.skill else None,
            title=a.title,
            description=a.description,
            priority=a.priority,
            estimated_effort_hours=a.estimated_effort_hours,
            generated_by=a.generated_by
        )
        for a in actions_records
    ]

    # Phase 2: Fetch Job-Level Match Summaries for all jobs in this search
    job_matches: List[JobMatchSummary] = []
    jca_records = db.query(JobCandidateAnalysis).filter(
        JobCandidateAnalysis.readiness_analysis_id == analysis.id
    ).all()

    for jca in jca_records:
        j = jca.job
        if not j:
            continue

        gaps = db.query(JobCandidateSkillGap).filter(JobCandidateSkillGap.analysis_id == jca.id).all()
        matched = [g.skill.name for g in gaps if g.gap_type == "matched" and g.skill]
        missing_req = [g.skill.name for g in gaps if g.gap_type == "missing" and g.job_importance == "required" and g.skill]
        missing_pref = [g.skill.name for g in gaps if g.gap_type == "missing" and g.job_importance != "required" and g.skill]
        weak = [g.skill.name for g in gaps if g.gap_type == "weak" and g.skill]

        job_matches.append(JobMatchSummary(
            job_id=j.id,
            title=j.title,
            company_name=j.company_name,
            location=j.location,
            apply_url=j.apply_url,
            posted_at=j.posted_at,
            match_score=jca.match_score,
            required_match_score=jca.required_match_score,
            preferred_match_score=jca.preferred_match_score,
            total_required_skills=jca.total_required_skills,
            matched_required_skills=jca.matched_required_skills,
            missing_required_skills=jca.missing_required_skills,
            weak_required_skills=jca.weak_required_skills,
            total_preferred_skills=jca.total_preferred_skills,
            matched_preferred_skills=jca.matched_preferred_skills,
            missing_preferred_skills=jca.missing_preferred_skills,
            weak_preferred_skills=jca.weak_preferred_skills,
            matched_skills=matched,
            missing_required=missing_req,
            missing_preferred=missing_pref,
            weak_skills=weak
        ))

    job_matches.sort(key=lambda x: x.match_score, reverse=True)

    # Phase 2: Market Recommendations recognizing recurring gaps
    market_recs = recommendation_service.generate_market_recommendations(
        market_stats=[m.model_dump() for m in market_skills],
        gaps=[g.model_dump() for g in all_gaps],
        job_analyses=[
            {
                "job_id": jca.job_id,
                "gaps": [
                    {"skill_id": g.skill_id, "gap_type": g.gap_type}
                    for g in db.query(JobCandidateSkillGap).filter(JobCandidateSkillGap.analysis_id == jca.id).all()
                ]
            }
            for jca in jca_records
        ],
        candidate_skills=[]
    )

    market_recommendation_items = [
        MarketRecommendationItem(
            skill_id=r.get("skill_id"),
            skill_name=r.get("skill_name", "Skill"),
            priority=r.get("priority", 1),
            why_it_matters=r.get("why_it_matters", ""),
            current_state=r.get("current_state", ""),
            recommended_next_step=r.get("recommended_next_step", ""),
            practical_action=r.get("practical_action", ""),
            evidence=r.get("evidence", ""),
            market_frequency_pct=r.get("market_frequency_pct", 50.0),
            recurring_jobs_count=r.get("recurring_jobs_count", 1),
            total_jobs_analyzed=r.get("total_jobs_analyzed", jobs_analyzed)
        )
        for r in market_recs
    ]

    return AnalysisResponse(
        id=analysis.id,
        status=analysis.status,
        target_role=role_name,
        location=location,
        jobs_analyzed=jobs_analyzed,
        readiness_score=analysis.readiness_score,
        summary=analysis.summary,
        created_at=analysis.created_at,
        market_skills=market_skills,
        gaps=all_gaps,
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        action_items=action_items,
        market_recommendations=market_recommendation_items,
        job_matches=job_matches
    )


@router.get("/{analysis_id}/jobs", response_model=List[JobMatchSummary])
def get_analysis_jobs(analysis_id: str, db: Session = Depends(get_db)):
    """
    Retrieve all job-specific match analyses associated with a market scan.
    """
    res = get_analysis_by_id(analysis_id=analysis_id, db=db)
    return res.job_matches


@router.get("/{analysis_id}/recommendations", response_model=List[MarketRecommendationItem])
def get_analysis_recommendations(analysis_id: str, db: Session = Depends(get_db)):
    """
    Retrieve synthesized market-level recommendations recognizing recurring gaps.
    """
    res = get_analysis_by_id(analysis_id=analysis_id, db=db)
    return res.market_recommendations


@router.get("/{analysis_id}/diff", response_model=WhatChangedResponse)
def get_analysis_diff(
    analysis_id: str,
    baseline_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve deterministic 'What Changed?' comparison between current analysis and previous baseline.
    """
    try:
        return progress_intelligence_service.compare_analyses(
            db=db,
            current_analysis_id=analysis_id,
            previous_analysis_id=baseline_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{analysis_id}/feedback", response_model=CandidateFeedbackReportResponse)
def get_candidate_feedback(analysis_id: str, db: Session = Depends(get_db)):
    """
    Retrieve comprehensive structured candidate intelligence report:
    Current Position, Strongest Areas, Biggest Gaps, What Changed, Market Signals, Action Plan.
    """
    try:
        return progress_intelligence_service.get_candidate_feedback_report(
            db=db,
            analysis_id=analysis_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/user/history", response_model=List[AnalysisResponse])
def get_user_analyses_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analyses = db.query(ReadinessAnalysis).filter(
        ReadinessAnalysis.user_id == current_user.id
    ).order_by(ReadinessAnalysis.created_at.desc()).all()
    
    results = []
    for a in analyses:
        try:
            results.append(get_analysis_by_id(analysis_id=a.id, db=db))
        except Exception:
            continue
    return results

