from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Watchlist, Job, JobSkill, CandidateSkill, Skill, User
from app.services.job_match_service import job_match_service


class WatchlistService:
    @classmethod
    def add_to_watchlist(cls, db: Session, user_id: str, job_id: str, notes: Optional[str] = None) -> Watchlist:
        existing = db.query(Watchlist).filter(
            Watchlist.user_id == user_id,
            Watchlist.job_id == job_id
        ).first()
        if existing:
            if notes is not None:
                existing.notes = notes
                db.commit()
            return existing

        item = Watchlist(user_id=user_id, job_id=job_id, notes=notes)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @classmethod
    def remove_from_watchlist(cls, db: Session, user_id: str, job_id: str) -> bool:
        item = db.query(Watchlist).filter(
            Watchlist.user_id == user_id,
            Watchlist.job_id == job_id
        ).first()
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    @classmethod
    def get_user_watchlist_with_matches(cls, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve saved jobs with dynamically recalculated match scores based on candidate's current skills.
        """
        watchlist_items = db.query(Watchlist).filter(Watchlist.user_id == user_id).order_by(Watchlist.created_at.desc()).all()
        if not watchlist_items:
            return []

        user_skills = db.query(CandidateSkill).filter(CandidateSkill.user_id == user_id).all()
        candidate_skills_data = [
            {"name": cs.skill.name if cs.skill else "Skill", "proficiency": cs.proficiency, "years_experience": cs.years_experience}
            for cs in user_skills
        ]
        all_canonical_skills = db.query(Skill).all()
        candidate_lookup = job_match_service.build_candidate_skill_lookup(candidate_skills_data, all_canonical_skills)

        results = []
        for item in watchlist_items:
            job = item.job
            if not job:
                continue

            job_skill_records = db.query(JobSkill).filter(JobSkill.job_id == job.id).all()
            match_res = job_match_service.analyze_job_for_candidate(
                job_id=job.id,
                job_skills=job_skill_records,
                candidate_lookup=candidate_lookup
            )

            missing_req = [g["name"] for g in match_res["gaps"] if g["gap_type"] == "missing" and g["job_importance"] == "required"]
            matched_names = [g["name"] for g in match_res["gaps"] if g["gap_type"] == "matched"]

            results.append({
                "id": item.id,
                "watchlist_id": item.id,
                "job_id": job.id,
                "title": job.title,
                "company_name": job.company_name,
                "location": job.location,
                "remote_type": job.remote_type,
                "apply_url": job.apply_url,
                "status": job.status or "active",
                "saved_at": item.created_at,
                "last_checked_at": item.created_at,
                "last_seen_at": job.last_seen_at,
                "match_score": match_res["match_score"],
                "required_match_score": match_res["required_match_score"],
                "total_required_skills": match_res["total_required_skills"],
                "matched_required_skills": match_res["matched_required_skills"],
                "missing_required_skills": match_res["missing_required_skills"],
                "matched_skills": matched_names,
                "missing_skills": missing_req,
                "missing_required": missing_req,
                "notes": item.notes
            })

        return results


watchlist_service = WatchlistService()
