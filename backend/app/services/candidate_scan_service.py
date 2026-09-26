import zoneinfo
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import (
    User, CandidateProfile, CandidateSkill, Skill, Job, JobSkill,
    CandidateJobAlertSettings, CandidateJobScan, Notification
)
from app.services.job_match_service import job_match_service
from app.services.email_service import email_service
from app.core.config import settings
from app.core.logging import logger

DAYS_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6
}


class CandidateScanService:
    @staticmethod
    def calculate_next_scan_at(
        day_of_week: str = "monday",
        time_of_day: str = "10:00",
        timezone_str: str = "Asia/Kolkata",
        from_datetime: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate next scan timestamp with full timezone awareness.
        """
        try:
            tz = zoneinfo.ZoneInfo(timezone_str)
        except Exception:
            tz = zoneinfo.ZoneInfo("UTC")

        now = from_datetime or datetime.now(tz)
        if now.tzinfo is None:
            now = now.replace(tzinfo=tz)

        target_weekday = DAYS_MAP.get(day_of_week.lower(), 0)
        hour, minute = map(int, time_of_day.split(":"))

        # Candidate's target time today
        target_time_today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Days until next target weekday
        days_ahead = (target_weekday - now.weekday()) % 7

        if days_ahead == 0 and now >= target_time_today:
            days_ahead = 7  # Target time has already passed today, schedule for next week

        next_scan_local = target_time_today + timedelta(days=days_ahead)
        # Return UTC naive datetime for standardized PostgreSQL storage
        return next_scan_local.astimezone(zoneinfo.ZoneInfo("UTC")).replace(tzinfo=None)

    @classmethod
    def get_or_create_alert_settings(cls, db: Session, user_id: str) -> CandidateJobAlertSettings:
        settings = db.query(CandidateJobAlertSettings).filter(CandidateJobAlertSettings.user_id == user_id).first()
        if not settings:
            next_scan = cls.calculate_next_scan_at("monday", "10:00", "Asia/Kolkata")
            settings = CandidateJobAlertSettings(
                user_id=user_id,
                enabled=True,
                frequency="weekly",
                day_of_week="monday",
                time_of_day="10:00",
                timezone="Asia/Kolkata",
                minimum_match_score=80.0,
                email_enabled=True,
                in_app_enabled=True,
                next_scan_at=next_scan
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)
        return settings

    @classmethod
    def execute_candidate_scan(cls, db: Session, user_id: str, is_manual: bool = False) -> CandidateJobScan:
        """
        Perform a personalized candidate scan over newly added/updated jobs in the CareerRadar database.
        Runs deterministic match calculations, filters by candidate threshold, and issues alerts.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found.")

        alert_settings = cls.get_or_create_alert_settings(db, user_id)
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()

        scan_record = CandidateJobScan(
            user_id=user_id,
            started_at=datetime.utcnow(),
            status="processing"
        )
        db.add(scan_record)
        db.commit()
        db.refresh(scan_record)

        target_role = profile.role.name if profile and profile.role else "Software Developer"
        target_location = profile.target_location if profile else "India"

        # Fetch candidate skills & canonical lookup
        user_skills = db.query(CandidateSkill).filter(CandidateSkill.user_id == user_id).all()
        candidate_skills_data = [
            {"name": cs.skill.name if cs.skill else "Skill", "proficiency": cs.proficiency, "years_experience": cs.years_experience}
            for cs in user_skills
        ]
        all_canonical_skills = db.query(Skill).all()
        candidate_lookup = job_match_service.build_candidate_skill_lookup(candidate_skills_data, all_canonical_skills)

        # Scan window: jobs added or updated since last scan (or within last 7 days for first scan)
        recency_cutoff = datetime.utcnow() - timedelta(days=settings.MAX_JOB_AGE_DAYS)
        query = db.query(Job).filter(
            Job.status == "active",
            or_(
                Job.posted_at >= recency_cutoff,
                Job.last_seen_at >= recency_cutoff
            )
        )
        
        # If not a manual scan, filter by creation/update timestamp in candidate's window
        if not is_manual:
            scan_window_start = alert_settings.last_scan_at or (datetime.utcnow() - timedelta(days=7))
            query = query.filter(Job.updated_at >= scan_window_start)

        relevant_jobs = query.all()
        total_checked = len(relevant_jobs)

        matched_jobs_list = []
        jobs_above_threshold_count = 0

        for job in relevant_jobs:
            job_skill_records = db.query(JobSkill).filter(JobSkill.job_id == job.id).all()
            match_res = job_match_service.analyze_job_for_candidate(
                job_id=job.id,
                job_skills=job_skill_records,
                candidate_lookup=candidate_lookup
            )
            
            score = match_res["match_score"]
            is_above_threshold = score >= alert_settings.minimum_match_score

            if is_above_threshold:
                jobs_above_threshold_count += 1

            missing_req_names = [g["name"] for g in match_res["gaps"] if g["gap_type"] == "missing" and g["job_importance"] == "required"]
            
            matched_jobs_list.append({
                "job_id": job.id,
                "title": job.title,
                "company_name": job.company_name,
                "location": job.location or "India",
                "match_score": score,
                "missing_required": missing_req_names,
                "posted_at": job.posted_at,
                "is_above_threshold": is_above_threshold
            })

        # Sort: Highest match score first, then posted_at descending
        matched_jobs_list.sort(key=lambda x: (x["match_score"], x["posted_at"] or datetime.min), reverse=True)

        # 1. Create In-App Notification if enabled
        if alert_settings.in_app_enabled and matched_jobs_list:
            top_match = matched_jobs_list[0]
            notif = Notification(
                user_id=user_id,
                type="weekly_job_digest",
                title=f"🎯 {len(matched_jobs_list)} New Job Matches Found",
                message=f"We found {jobs_above_threshold_count} jobs with an {round(alert_settings.minimum_match_score)}%+ match. Top match: {top_match['title']} at {top_match['company_name']} ({top_match['match_score']}% Match).",
                data={
                    "total_new_jobs": len(matched_jobs_list),
                    "jobs_above_threshold": jobs_above_threshold_count,
                    "top_match_job_id": top_match["job_id"],
                    "top_match_score": top_match["match_score"]
                }
            )
            db.add(notif)

        # 2. Dispatch Email Digest if enabled
        email_sent = False
        if alert_settings.email_enabled and user.email and matched_jobs_list:
            email_sent = email_service.send_weekly_job_digest(
                to_email=user.email,
                candidate_name=user.display_name,
                target_role=target_role,
                location=target_location,
                total_new_jobs=len(matched_jobs_list),
                jobs_above_threshold=jobs_above_threshold_count,
                min_match_score=alert_settings.minimum_match_score,
                top_jobs=matched_jobs_list[:10]
            )

        # Update timestamps
        now_utc = datetime.utcnow()
        alert_settings.last_scan_at = now_utc
        alert_settings.next_scan_at = cls.calculate_next_scan_at(
            day_of_week=alert_settings.day_of_week,
            time_of_day=alert_settings.time_of_day,
            timezone_str=alert_settings.timezone,
            from_datetime=now_utc
        )

        scan_record.completed_at = now_utc
        scan_record.jobs_checked = total_checked
        scan_record.jobs_matched = len(matched_jobs_list)
        scan_record.jobs_above_threshold = jobs_above_threshold_count
        scan_record.email_sent = email_sent
        scan_record.status = "completed"
        db.commit()

        logger.info(f"[Candidate Scan] Completed scan for user {user.display_name}: {jobs_above_threshold_count}/{total_checked} above {alert_settings.minimum_match_score}% threshold.")
        return scan_record

    @classmethod
    def run_due_candidate_scans(cls, db: Session) -> int:
        """
        Identify candidates whose next_scan_at <= NOW and execute their scheduled scan.
        """
        now_utc = datetime.utcnow()
        due_settings = db.query(CandidateJobAlertSettings).filter(
            CandidateJobAlertSettings.enabled == True,
            CandidateJobAlertSettings.next_scan_at <= now_utc
        ).all()

        count = 0
        for setting in due_settings:
            try:
                cls.execute_candidate_scan(db, setting.user_id, is_manual=False)
                count += 1
            except Exception as e:
                logger.error(f"[Candidate Scan] Error scanning for user_id={setting.user_id}: {e}")
                continue
        return count


candidate_scan_service = CandidateScanService()
