from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.core.config import settings
from app.core.database import get_db
from app.api.deps import get_optional_current_user, get_current_user
from app.models import (
    User, Job, JobSkill, CandidateSkill, Skill,
    JobCandidateAnalysis, JobCandidateSkillGap, JobCandidateRecommendation,
    Watchlist, JobIngestionReport
)
from app.schemas.job import (
    JobDetailedAnalysisResponse, JobSkillItem,
    JobCandidateSkillGapItem, JobCandidateRecommendationItem,
    DatabaseJobItem, DatabaseJobSearchResponse,
    AdminRefreshResponse, AdminStatusResponse
)
from app.schemas.profile import CandidateSkillInput
from app.services.job_match_service import job_match_service
from app.services.recommendation_service import recommendation_service
from app.services.central_job_ingestion_service import central_job_ingestion_service

router = APIRouter(prefix="/jobs", tags=["Job-Level Skill Gap Analyses & Database Search"])


@router.get("/search", response_model=DatabaseJobSearchResponse)
def search_database_jobs(
    role: Optional[str] = Query(None, description="Job title / role keyword"),
    location: Optional[str] = Query(None, description="Location keyword"),
    remote_type: Optional[str] = Query(None, description="Remote type: remote, hybrid, on-site"),
    skills: Optional[str] = Query(None, description="Comma-separated skills list"),
    status: Optional[str] = Query("active", description="Job status: active, stale, all"),
    minimum_match: Optional[float] = Query(None, description="Minimum match score threshold (0-100)"),
    sort: Optional[str] = Query("match_score", description="Sort by: match_score, recent, relevance"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Search CareerRadar's centralized job database.
    Does NOT invoke external SerpApi search.
    Computes deterministic candidate match scores if user is authenticated.
    Enforces <= 60-day recency window (current/previous month) on active jobs.
    """
    query = db.query(Job)

    if status and status != "all":
        query = query.filter(Job.status == status)
        if status == "active":
            recency_cutoff = datetime.utcnow() - timedelta(days=settings.MAX_JOB_AGE_DAYS)
            query = query.filter(
                or_(
                    Job.posted_at >= recency_cutoff,
                    Job.last_seen_at >= recency_cutoff
                )
            )

    if role:
        query = query.filter(Job.title.ilike(f"%{role.strip()}%"))

    if location:
        query = query.filter(Job.location.ilike(f"%{location.strip()}%"))

    if remote_type and remote_type != "all":
        query = query.filter(Job.remote_type.ilike(f"%{remote_type.strip()}%"))

    # If filtering by specific skills
    if skills:
        skill_names = [s.strip().lower() for s in skills.split(",") if s.strip()]
        if skill_names:
            query = query.join(JobSkill).join(Skill).filter(
                or_(*[Skill.name.ilike(f"%{sk}%") for sk in skill_names])
            ).distinct()

    all_jobs = query.all()

    # Get saved job ids for current user
    saved_job_ids = set()
    candidate_lookup = {}
    if current_user:
        user_saved = db.query(Watchlist.job_id).filter(Watchlist.user_id == current_user.id).all()
        saved_job_ids = {row[0] for row in user_saved}

        user_skills = db.query(CandidateSkill).filter(CandidateSkill.user_id == current_user.id).all()
        candidate_skills_data = [
            {"name": cs.skill.name if cs.skill else "Skill", "proficiency": cs.proficiency, "years_experience": cs.years_experience}
            for cs in user_skills
        ]
        all_canonical_skills = db.query(Skill).all()
        candidate_lookup = job_match_service.build_candidate_skill_lookup(candidate_skills_data, all_canonical_skills)

    # Process and compute match scores
    processed_jobs = []
    for job in all_jobs:
        job_skills = db.query(JobSkill).filter(JobSkill.job_id == job.id).all()
        skills_items = [
            JobSkillItem(
                skill_id=js.skill_id,
                name=js.skill.name if js.skill else "Skill",
                category=js.skill.category if js.skill else "General",
                importance=js.importance,
                mention_count=js.mention_count,
                evidence=js.evidence
            )
            for js in job_skills
        ]

        match_score = None
        missing_skills = []
        matched_skills = []

        if current_user and candidate_lookup:
            analysis = job_match_service.analyze_job_for_candidate(
                job_id=job.id,
                job_skills=job_skills,
                candidate_lookup=candidate_lookup
            )
            match_score = analysis.get("match_score", 0.0)
            for g in analysis.get("gaps", []):
                if g["gap_type"] == "matched":
                    matched_skills.append(g["name"])
                elif g["gap_type"] in ["missing", "weak"]:
                    missing_skills.append(g["name"])

        # Filter by minimum match if requested
        if minimum_match is not None:
            if match_score is None or match_score < minimum_match:
                continue

        processed_jobs.append(
            DatabaseJobItem(
                id=job.id,
                title=job.title,
                company_name=job.company_name,
                location=job.location,
                remote_type=job.remote_type,
                description=job.description,
                apply_url=job.apply_url,
                status=job.status or "active",
                first_seen_at=job.first_seen_at,
                last_seen_at=job.last_seen_at,
                posted_at=job.posted_at,
                updated_at=job.updated_at,
                skills=skills_items,
                match_score=match_score,
                missing_skills=missing_skills[:5],
                matched_skills=matched_skills[:5],
                is_saved=job.id in saved_job_ids
            )
        )

    # Sorting
    if sort == "match_score":
        processed_jobs.sort(key=lambda x: (x.match_score is not None, x.match_score or 0.0, x.posted_at or x.first_seen_at), reverse=True)
    elif sort == "recent":
        processed_jobs.sort(key=lambda x: (x.posted_at or x.first_seen_at or x.updated_at), reverse=True)
    else:  # relevance
        processed_jobs.sort(key=lambda x: (x.match_score or 0.0, len(x.skills)), reverse=True)

    # Pagination
    total_count = len(processed_jobs)
    total_pages = max(1, (total_count + limit - 1) // limit)
    offset = (page - 1) * limit
    paginated_jobs = processed_jobs[offset : offset + limit]

    # Get last ingestion time
    last_report = db.query(JobIngestionReport).order_by(JobIngestionReport.completed_at.desc()).first()
    last_refreshed_at = last_report.completed_at if last_report else None

    return DatabaseJobSearchResponse(
        total=total_count,
        page=page,
        limit=limit,
        total_pages=total_pages,
        jobs=paginated_jobs,
        applied_filters={
            "role": role,
            "location": location,
            "remote_type": remote_type,
            "skills": skills,
            "status": status,
            "minimum_match": minimum_match,
            "sort": sort
        },
        database_last_refreshed_at=last_refreshed_at
    )


@router.post("/admin/refresh", response_model=AdminRefreshResponse)
def trigger_market_database_refresh(
    background_tasks: BackgroundTasks,
    run_async: bool = Query(True, description="Run in background"),
    db: Session = Depends(get_db)
):
    """
    Trigger central market database ingestion from SerpApi across configured roles and locations.
    Idempotent and updates existing job records.
    """
    if run_async:
        background_tasks.add_task(central_job_ingestion_service.refresh_market_database)
        return AdminRefreshResponse(
            status="started",
            message="Central job database refresh launched in background."
        )
    else:
        report = central_job_ingestion_service.refresh_market_database(db=db)
        return AdminRefreshResponse(
            status="completed" if report.status == "completed" else "failed",
            message=f"Database refresh finished with status: {report.status}",
            report_id=report.id,
            total_found=report.total_jobs_found,
            total_inserted=report.jobs_inserted,
            total_updated=report.jobs_updated,
            total_stale=report.jobs_marked_stale,
            errors_count=len(report.errors) if report.errors else 0
        )


@router.get("/admin/status", response_model=AdminStatusResponse)
def get_job_database_admin_status(
    db: Session = Depends(get_db)
):
    """
    Internal system monitoring view for central job database ingestion and freshness.
    """
    active_count = db.query(Job).filter(Job.status == "active").count()
    stale_count = db.query(Job).filter(Job.status == "stale").count()
    expired_count = db.query(Job).filter(Job.status == "expired").count()
    total_count = db.query(Job).count()

    recent_reports_query = db.query(JobIngestionReport).order_by(JobIngestionReport.started_at.desc()).limit(10).all()
    reports_data = [
        {
            "id": r.id,
            "status": r.status,
            "trigger_type": r.trigger_type,
            "started_at": r.started_at,
            "completed_at": r.completed_at,
            "duration_seconds": r.duration_seconds,
            "roles_searched": r.roles_searched,
            "locations_searched": r.locations_searched,
            "total_jobs_found": r.total_jobs_found,
            "jobs_inserted": r.jobs_inserted,
            "jobs_updated": r.jobs_updated,
            "jobs_marked_stale": r.jobs_marked_stale,
            "errors": r.errors
        }
        for r in recent_reports_query
    ]

    last_refresh = recent_reports_query[0].completed_at if (recent_reports_query and recent_reports_query[0].completed_at) else None

    return AdminStatusResponse(
        total_active_jobs=active_count,
        total_stale_jobs=stale_count,
        total_expired_jobs=expired_count,
        total_jobs=total_count,
        last_refresh_at=last_refresh,
        recent_reports=reports_data
    )



@router.get("/{job_id}/analysis", response_model=JobDetailedAnalysisResponse)
def get_job_analysis(
    job_id: str,
    analysis_id: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve job-specific skill gap analysis, match score breakdown, and personalized recommendations.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    # Find existing JobCandidateAnalysis if exists
    query = db.query(JobCandidateAnalysis).filter(JobCandidateAnalysis.job_id == job_id)
    if analysis_id:
        query = query.filter(JobCandidateAnalysis.readiness_analysis_id == analysis_id)
    elif current_user:
        query = query.filter(JobCandidateAnalysis.user_id == current_user.id)

    jca = query.order_by(JobCandidateAnalysis.created_at.desc()).first()

    # If no stored analysis exists, perform on-the-fly analysis using candidate's profile
    if not jca:
        candidate_skills_data = []
        if current_user:
            user_skills = db.query(CandidateSkill).filter(CandidateSkill.user_id == current_user.id).all()
            candidate_skills_data = [
                {"name": cs.skill.name if cs.skill else "Skill", "proficiency": cs.proficiency, "years_experience": cs.years_experience}
                for cs in user_skills
            ]

        all_canonical_skills = db.query(Skill).all()
        candidate_lookup = job_match_service.build_candidate_skill_lookup(candidate_skills_data, all_canonical_skills)
        job_skills = db.query(JobSkill).filter(JobSkill.job_id == job_id).all()
        
        analysis_result = job_match_service.analyze_job_for_candidate(
            job_id=job_id,
            job_skills=job_skills,
            candidate_lookup=candidate_lookup
        )
        recommendations = recommendation_service.generate_job_recommendations(
            job=job,
            gaps=analysis_result["gaps"],
            candidate_skills=candidate_skills_data
        )

        return _build_response_from_dict(job, analysis_result, recommendations)

    # Return stored analysis
    gaps_records = db.query(JobCandidateSkillGap).filter(JobCandidateSkillGap.analysis_id == jca.id).all()
    recs_records = db.query(JobCandidateRecommendation).filter(JobCandidateRecommendation.analysis_id == jca.id).order_by(JobCandidateRecommendation.priority).all()
    job_skills_records = db.query(JobSkill).filter(JobSkill.job_id == job_id).all()

    skills_list = [
        JobSkillItem(
            skill_id=js.skill_id,
            name=js.skill.name if js.skill else "Skill",
            category=js.skill.category if js.skill else "General",
            importance=js.importance,
            mention_count=js.mention_count,
            evidence=js.evidence
        )
        for js in job_skills_records
    ]

    all_gaps = []
    matched_skills = []
    missing_required = []
    missing_preferred = []
    weak_gaps = []

    for g in gaps_records:
        sk = g.skill
        gap_item = JobCandidateSkillGapItem(
            id=g.id,
            skill_id=g.skill_id,
            name=sk.name if sk else "Skill",
            category=sk.category if sk else "General",
            gap_type=g.gap_type,
            job_importance=g.job_importance,
            candidate_proficiency=g.candidate_proficiency,
            priority_score=g.priority_score,
            evidence=g.evidence
        )
        all_gaps.append(gap_item)
        if g.gap_type == "matched":
            matched_skills.append(gap_item)
        elif g.gap_type == "weak":
            weak_gaps.append(gap_item)
        elif g.gap_type == "missing":
            if g.job_importance == "required":
                missing_required.append(gap_item)
            else:
                missing_preferred.append(gap_item)

    recommendations_list = [
        JobCandidateRecommendationItem(
            id=r.id,
            skill_id=r.skill_id,
            skill_name=r.skill.name if r.skill else None,
            priority=r.priority,
            why_it_matters=r.why_it_matters,
            current_state=r.current_state,
            recommended_next_step=r.recommended_next_step,
            practical_action=r.practical_action,
            evidence=r.evidence,
            generated_by=r.generated_by
        )
        for r in recs_records
    ]

    return JobDetailedAnalysisResponse(
        job_id=job.id,
        title=job.title,
        company_name=job.company_name,
        location=job.location,
        remote_type=job.remote_type,
        description=job.description,
        apply_url=job.apply_url,
        posted_at=job.posted_at,
        match_score=jca.match_score,
        required_match_score=jca.required_match_score,
        preferred_match_score=jca.preferred_match_score,
        total_skills_count=len(skills_list),
        total_required_skills=jca.total_required_skills,
        matched_required_skills=jca.matched_required_skills,
        missing_required_skills=jca.missing_required_skills,
        weak_required_skills=jca.weak_required_skills,
        total_preferred_skills=jca.total_preferred_skills,
        matched_preferred_skills=jca.matched_preferred_skills,
        missing_preferred_skills=jca.missing_preferred_skills,
        weak_preferred_skills=jca.weak_preferred_skills,
        skills=skills_list,
        gaps=all_gaps,
        matched_skills=matched_skills,
        missing_required_gaps=missing_required,
        missing_preferred_gaps=missing_preferred,
        weak_gaps=weak_gaps,
        recommendations=recommendations_list
    )


@router.post("/{job_id}/analyze", response_model=JobDetailedAnalysisResponse)
def analyze_specific_job(
    job_id: str,
    candidate_skills: List[CandidateSkillInput],
    db: Session = Depends(get_db)
):
    """
    On-demand ad-hoc deterministic gap analysis for a specific job against provided skills.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    all_canonical_skills = db.query(Skill).all()
    skills_data = [s.model_dump() for s in candidate_skills]
    candidate_lookup = job_match_service.build_candidate_skill_lookup(skills_data, all_canonical_skills)
    job_skills = db.query(JobSkill).filter(JobSkill.job_id == job_id).all()

    analysis_result = job_match_service.analyze_job_for_candidate(
        job_id=job_id,
        job_skills=job_skills,
        candidate_lookup=candidate_lookup
    )
    recommendations = recommendation_service.generate_job_recommendations(
        job=job,
        gaps=analysis_result["gaps"],
        candidate_skills=skills_data
    )

    return _build_response_from_dict(job, analysis_result, recommendations)


def _build_response_from_dict(job: Job, result: dict, recs: list) -> JobDetailedAnalysisResponse:
    all_gaps = []
    matched_skills = []
    missing_required = []
    missing_preferred = []
    weak_gaps = []

    for g in result.get("gaps", []):
        item = JobCandidateSkillGapItem(
            skill_id=g["skill_id"],
            name=g["name"],
            category=g.get("category", "General"),
            gap_type=g["gap_type"],
            job_importance=g["job_importance"],
            candidate_proficiency=g.get("candidate_proficiency"),
            priority_score=g["priority_score"],
            evidence=g["evidence"]
        )
        all_gaps.append(item)
        if g["gap_type"] == "matched":
            matched_skills.append(item)
        elif g["gap_type"] == "weak":
            weak_gaps.append(item)
        elif g["gap_type"] == "missing":
            if g["job_importance"] == "required":
                missing_required.append(item)
            else:
                missing_preferred.append(item)

    rec_items = [
        JobCandidateRecommendationItem(
            skill_id=r.get("skill_id"),
            skill_name=r.get("skill_name"),
            priority=r.get("priority", 1),
            why_it_matters=r.get("why_it_matters", ""),
            current_state=r.get("current_state", ""),
            recommended_next_step=r.get("recommended_next_step", ""),
            practical_action=r.get("practical_action", ""),
            evidence=r.get("evidence", ""),
            generated_by=r.get("generated_by", "rule")
        )
        for r in recs
    ]

    return JobDetailedAnalysisResponse(
        job_id=job.id,
        title=job.title,
        company_name=job.company_name,
        location=job.location,
        remote_type=job.remote_type,
        description=job.description,
        apply_url=job.apply_url,
        posted_at=job.posted_at,
        match_score=result["match_score"],
        required_match_score=result["required_match_score"],
        preferred_match_score=result["preferred_match_score"],
        total_skills_count=result["total_skills"],
        total_required_skills=result["total_required_skills"],
        matched_required_skills=result["matched_required_skills"],
        missing_required_skills=result["missing_required_skills"],
        weak_required_skills=result["weak_required_skills"],
        total_preferred_skills=result["total_preferred_skills"],
        matched_preferred_skills=result["matched_preferred_skills"],
        missing_preferred_skills=result["missing_preferred_skills"],
        weak_preferred_skills=result["weak_preferred_skills"],
        skills=[],
        gaps=all_gaps,
        matched_skills=matched_skills,
        missing_required_gaps=missing_required,
        missing_preferred_gaps=missing_preferred,
        weak_gaps=weak_gaps,
        recommendations=rec_items
    )
