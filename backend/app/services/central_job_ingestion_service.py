from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Job, JobSkill, Skill, JobIngestionReport
from app.integrations.serpapi.client import serpapi_client
from app.services.job_normalization_service import job_normalization_service
from app.services.skill_extraction_service import skill_extraction_service
from app.core.config import settings
from app.core.logging import logger

DEFAULT_INGESTION_ROLES = [
    "Full Stack Developer",
    "Frontend Developer",
    "Backend Developer",
    "Software Engineer",
    "Python Developer",
    "React Developer",
    "Node.js Developer",
    "DevOps Engineer"
]

DEFAULT_INGESTION_LOCATIONS = [
    "India",
    "Ahmedabad",
    "Bengaluru",
    "Delhi",
    "Mumbai",
    "Hyderabad",
    "Pune",
    "Remote"
]


class CentralJobIngestionService:
    @classmethod
    async def refresh_central_job_database(
        cls,
        db: Session,
        roles: Optional[List[str]] = None,
        locations: Optional[List[str]] = None
    ) -> JobIngestionReport:
        """
        Execute scheduled/manual central job database refresh across configured roles and geographic locations.
        Idempotent: Updates existing jobs, inserts new ones, extracts skills, and marks stale listings.
        """
        target_roles = roles or DEFAULT_INGESTION_ROLES
        target_locations = locations or DEFAULT_INGESTION_LOCATIONS

        report = JobIngestionReport(
            started_at=datetime.utcnow(),
            roles_queried=len(target_roles),
            locations_queried=len(target_locations),
            status="processing"
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        logger.info(f"[Central Ingestion] Starting central market refresh: {len(target_roles)} roles x {len(target_locations)} locations")

        all_canonical_skills = db.query(Skill).all()
        total_fetched = 0
        new_inserted = 0
        existing_updated = 0

        # Execute searches across configured matrix
        for role in target_roles:
            for loc in target_locations[:2]:  # Query primary regions per cycle for balanced API usage
                try:
                    raw_jobs = await serpapi_client.search_google_jobs(query=role, location=loc)
                    total_fetched += len(raw_jobs)

                    for idx, rj in enumerate(raw_jobs):
                        norm = job_normalization_service.normalize_job(rj)

                        # Check deduplication by provider_job_id or (title + company)
                        existing_job = None
                        if norm["provider_job_id"]:
                            existing_job = db.query(Job).filter(
                                Job.provider == norm["provider"],
                                Job.provider_job_id == norm["provider_job_id"]
                            ).first()
                        
                        if not existing_job:
                            existing_job = db.query(Job).filter(
                                Job.normalized_title == norm["normalized_title"],
                                Job.company_name == norm["company_name"]
                            ).first()

                        if existing_job:
                            # Update existing record
                            existing_job.last_seen_at = datetime.utcnow()
                            existing_job.status = "active"
                            target_job = existing_job
                            existing_updated += 1
                        else:
                            # Insert new record
                            new_job = Job(
                                provider=norm["provider"],
                                provider_job_id=norm["provider_job_id"],
                                title=norm["title"],
                                normalized_title=norm["normalized_title"],
                                company_name=norm["company_name"],
                                location=norm["location"],
                                remote_type=norm["remote_type"],
                                description=norm["description"],
                                apply_url=norm["apply_url"],
                                source_url=norm["source_url"],
                                posted_at=norm["posted_at"],
                                status="active",
                                raw_payload=norm["raw_payload"]
                            )
                            db.add(new_job)
                            db.flush()
                            target_job = new_job
                            new_inserted += 1

                        # Extract & update skills
                        full_text = f"{target_job.title} {target_job.description or ''}"
                        extracted = skill_extraction_service.extract_skills_from_text(full_text, all_canonical_skills)
                        for sk, mentions, method in extracted:
                            existing_js = db.query(JobSkill).filter(
                                JobSkill.job_id == target_job.id,
                                JobSkill.skill_id == sk.id
                            ).first()
                            if not existing_js:
                                db.add(JobSkill(
                                    job_id=target_job.id,
                                    skill_id=sk.id,
                                    mention_count=mentions,
                                    extraction_method=method,
                                    importance="required" if mentions > 1 or idx < 2 else "preferred"
                                ))

                    db.commit()
                except Exception as e:
                    logger.error(f"[Central Ingestion] Error querying role '{role}' in '{loc}': {e}")
                    continue

        # Mark stale jobs (jobs not seen within configured TTL threshold or posted > MAX_JOB_AGE_DAYS ago)
        stale_cutoff = datetime.utcnow() - timedelta(days=settings.MAX_JOB_AGE_DAYS)
        stale_jobs_count = db.query(Job).filter(
            Job.status == "active",
            or_(
                Job.posted_at < stale_cutoff,
                Job.last_seen_at < stale_cutoff
            )
        ).update({"status": "stale"}, synchronize_session=False)

        report.completed_at = datetime.utcnow()
        report.total_jobs_fetched = total_fetched
        report.new_jobs_inserted = new_inserted
        report.existing_jobs_updated = existing_updated
        report.jobs_marked_stale = stale_jobs_count
        report.status = "completed"
        db.commit()

        logger.info(f"[Central Ingestion] Completed: {new_inserted} new, {existing_updated} updated, {stale_jobs_count} marked stale.")
        return report


central_job_ingestion_service = CentralJobIngestionService()
