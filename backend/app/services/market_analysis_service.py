from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import (
    User, Role, Skill, Job, SearchRun, SearchRunJob, JobSkill,
    MarketSnapshot, MarketSkillStat, ReadinessAnalysis, ReadinessGap, ActionItem, CandidateSkill,
    JobCandidateAnalysis, JobCandidateSkillGap, JobCandidateRecommendation
)
from app.integrations.serpapi.client import serpapi_client
from app.integrations.llm.client import llm_client
from app.services.job_normalization_service import job_normalization_service
from app.services.skill_extraction_service import skill_extraction_service
from app.services.readiness_service import readiness_service
from app.services.job_match_service import job_match_service
from app.services.recommendation_service import recommendation_service
from app.core.logging import logger


class MarketAnalysisService:
    @classmethod
    async def run_market_analysis(
        cls,
        db: Session,
        user_id: Optional[str],
        target_role: str,
        location: str,
        skills_input: List[Dict[str, Any]],
        experience_years: int = 0
    ) -> ReadinessAnalysis:
        logger.info(f"Starting market analysis for role='{target_role}', location='{location}'")

        # 1. Fetch or create Role
        norm_role_name = target_role.strip().lower()
        role = db.query(Role).filter(Role.normalized_name == norm_role_name).first()
        if not role:
            role = Role(name=target_role.strip().title(), normalized_name=norm_role_name)
            db.add(role)
            db.flush()

        # 2. Create SearchRun
        search_run = SearchRun(
            user_id=user_id,
            role_id=role.id,
            query=target_role,
            location=location,
            status="searching",
            requested_at=datetime.utcnow()
        )
        db.add(search_run)
        db.commit()
        db.refresh(search_run)

        # 3. Call Live Jobs Provider (SerpApi Google Jobs)
        raw_jobs = await serpapi_client.search_google_jobs(query=target_role, location=location)
        search_run.status = "processing"
        search_run.result_count = len(raw_jobs)
        db.commit()

        # 4. Fetch all Canonical Skills for extraction
        all_canonical_skills = db.query(Skill).all()

        # 5. Normalize, Deduplicate & Store Jobs
        saved_jobs: List[Job] = []
        for idx, rj in enumerate(raw_jobs):
            norm_job_data = job_normalization_service.normalize_job(rj)
            
            # Check deduplication by provider + provider_job_id or (title + company)
            existing_job = None
            if norm_job_data["provider_job_id"]:
                existing_job = db.query(Job).filter(
                    Job.provider == norm_job_data["provider"],
                    Job.provider_job_id == norm_job_data["provider_job_id"]
                ).first()
            
            if not existing_job:
                existing_job = db.query(Job).filter(
                    Job.normalized_title == norm_job_data["normalized_title"],
                    Job.company_name == norm_job_data["company_name"]
                ).first()

            if not existing_job:
                new_job = Job(
                    provider=norm_job_data["provider"],
                    provider_job_id=norm_job_data["provider_job_id"],
                    title=norm_job_data["title"],
                    normalized_title=norm_job_data["normalized_title"],
                    company_name=norm_job_data["company_name"],
                    location=norm_job_data["location"],
                    remote_type=norm_job_data["remote_type"],
                    description=norm_job_data["description"],
                    apply_url=norm_job_data["apply_url"],
                    source_url=norm_job_data["source_url"],
                    posted_at=norm_job_data.get("posted_at"),
                    raw_payload=norm_job_data["raw_payload"]
                )
                db.add(new_job)
                db.flush()
                target_job = new_job
            else:
                existing_job.last_seen_at = datetime.utcnow()
                target_job = existing_job

            saved_jobs.append(target_job)

            # Link job to search run
            existing_sr_job = db.query(SearchRunJob).filter(
                SearchRunJob.search_run_id == search_run.id,
                SearchRunJob.job_id == target_job.id
            ).first()
            if not existing_sr_job:
                db.add(SearchRunJob(search_run_id=search_run.id, job_id=target_job.id, rank=idx+1))

            # Extract skills from job description & title
            full_job_text = f"{target_job.title} {target_job.description or ''}"
            extracted_skills = skill_extraction_service.extract_skills_from_text(full_job_text, all_canonical_skills)
            
            for sk, mentions, method in extracted_skills:
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

        # 6. Create Market Snapshot
        total_jobs_analyzed = len(saved_jobs)
        snapshot = MarketSnapshot(
            search_run_id=search_run.id,
            role_id=role.id,
            location=location,
            jobs_analyzed=total_jobs_analyzed,
            generated_at=datetime.utcnow()
        )
        db.add(snapshot)
        db.flush()

        # 7. Calculate Market Statistics per Skill
        skill_counts: Dict[str, Dict[str, Any]] = {}
        for job in saved_jobs:
            job_skill_records = db.query(JobSkill).filter(JobSkill.job_id == job.id).all()
            for js in job_skill_records:
                if js.skill_id not in skill_counts:
                    sk_obj = db.query(Skill).filter(Skill.id == js.skill_id).first()
                    skill_counts[js.skill_id] = {
                        "skill_id": js.skill_id,
                        "name": sk_obj.name if sk_obj else "Skill",
                        "category": sk_obj.category if sk_obj else "General",
                        "jobs_count": 0,
                        "total_mentions": 0
                    }
                skill_counts[js.skill_id]["jobs_count"] += 1
                skill_counts[js.skill_id]["total_mentions"] += js.mention_count

        market_stats_list = []
        market_frequencies: Dict[str, float] = {}
        for sk_id, data in skill_counts.items():
            freq_pct = (data["jobs_count"] / total_jobs_analyzed) * 100.0 if total_jobs_analyzed > 0 else 0.0
            stat = MarketSkillStat(
                snapshot_id=snapshot.id,
                skill_id=sk_id,
                jobs_with_skill=data["jobs_count"],
                total_mentions=data["total_mentions"],
                frequency_pct=round(freq_pct, 1),
                market_importance_score=round(freq_pct, 1)
            )
            db.add(stat)
            market_frequencies[sk_id] = round(freq_pct, 1)
            market_frequencies[data["name"].lower()] = round(freq_pct, 1)
            market_stats_list.append({
                "skill_id": sk_id,
                "name": data["name"],
                "category": data["category"],
                "frequency_pct": round(freq_pct, 1),
                "market_importance_score": round(freq_pct, 1),
                "jobs_with_skill": data["jobs_count"],
                "total_mentions": data["total_mentions"]
            })

        db.commit()

        # 8. Build Candidate Lookup using Alias Resolution
        candidate_lookup = job_match_service.build_candidate_skill_lookup(skills_input, all_canonical_skills)

        # 9. Deterministic Readiness & Global Gap Calculation (Phase 1 Market Level)
        readiness_result = readiness_service.calculate_readiness_score(market_stats_list, candidate_lookup)

        # 10. LLM Structured Evidence Call (Strictly explanatory)
        evidence_payload = {
            "target_role": target_role,
            "location": location,
            "jobs_analyzed": total_jobs_analyzed,
            "readiness_score": readiness_result["readiness_score"],
            "market_skills": sorted(market_stats_list, key=lambda x: x["frequency_pct"], reverse=True)[:10],
            "matched_skills": readiness_result["matched"][:5],
            "weak_skills": readiness_result["weak"][:5],
            "missing_skills": readiness_result["missing"][:5]
        }
        ai_response = await llm_client.generate_market_explanation(evidence_payload)

        # 11. Store ReadinessAnalysis & Gaps
        analysis = ReadinessAnalysis(
            user_id=user_id or "anonymous",
            snapshot_id=snapshot.id,
            readiness_score=readiness_result["readiness_score"],
            status="completed",
            summary=ai_response.get("summary")
        )
        db.add(analysis)
        db.flush()

        # Save Global Readiness Gaps
        for g in readiness_result["gaps"]:
            db.add(ReadinessGap(
                analysis_id=analysis.id,
                skill_id=g["skill_id"],
                gap_type=g["gap_type"],
                market_frequency_pct=g["market_frequency_pct"],
                importance_score=g["importance_score"],
                candidate_proficiency=g["candidate_proficiency"],
                priority_score=g["priority_score"],
                explanation=g.get("explanation")
            ))

        # Save Action Items
        for ai in ai_response.get("action_items", []):
            sk_obj = None
            if ai.get("skill_name"):
                sk_obj = db.query(Skill).filter(Skill.normalized_name == ai["skill_name"].lower()).first()

            db.add(ActionItem(
                analysis_id=analysis.id,
                skill_id=sk_obj.id if sk_obj else None,
                title=ai.get("title", "Action Item"),
                description=ai.get("description", ""),
                priority=ai.get("priority", 1),
                estimated_effort_hours=ai.get("estimated_effort_hours", 10),
                generated_by="ai"
            ))

        # =========================================================================
        # PHASE 2: Deterministic Job-Level Match Analysis & Recommendations per Job
        # =========================================================================
        job_analysis_summaries = []
        for target_job in saved_jobs:
            job_skill_records = db.query(JobSkill).filter(JobSkill.job_id == target_job.id).all()
            
            job_analysis_result = job_match_service.analyze_job_for_candidate(
                job_id=target_job.id,
                job_skills=job_skill_records,
                candidate_lookup=candidate_lookup,
                market_frequencies=market_frequencies
            )
            job_analysis_summaries.append(job_analysis_result)

            # Persist JobCandidateAnalysis
            jca = JobCandidateAnalysis(
                job_id=target_job.id,
                user_id=user_id,
                readiness_analysis_id=analysis.id,
                match_score=job_analysis_result["match_score"],
                required_match_score=job_analysis_result["required_match_score"],
                preferred_match_score=job_analysis_result["preferred_match_score"],
                total_required_skills=job_analysis_result["total_required_skills"],
                matched_required_skills=job_analysis_result["matched_required_skills"],
                missing_required_skills=job_analysis_result["missing_required_skills"],
                weak_required_skills=job_analysis_result["weak_required_skills"],
                total_preferred_skills=job_analysis_result["total_preferred_skills"],
                matched_preferred_skills=job_analysis_result["matched_preferred_skills"],
                missing_preferred_skills=job_analysis_result["missing_preferred_skills"],
                weak_preferred_skills=job_analysis_result["weak_preferred_skills"],
            )
            db.add(jca)
            db.flush()

            # Persist JobCandidateSkillGap
            for gap in job_analysis_result["gaps"]:
                db.add(JobCandidateSkillGap(
                    analysis_id=jca.id,
                    skill_id=gap["skill_id"],
                    gap_type=gap["gap_type"],
                    job_importance=gap["job_importance"],
                    candidate_proficiency=gap.get("candidate_proficiency"),
                    priority_score=gap["priority_score"],
                    evidence=gap["evidence"]
                ))

            # Generate and Persist Job-Specific Actionable Recommendations
            job_recs = recommendation_service.generate_job_recommendations(
                job=target_job,
                gaps=job_analysis_result["gaps"],
                candidate_skills=skills_input,
                limit=3
            )
            for rec in job_recs:
                db.add(JobCandidateRecommendation(
                    analysis_id=jca.id,
                    skill_id=rec.get("skill_id"),
                    priority=rec.get("priority", 1),
                    why_it_matters=rec.get("why_it_matters", ""),
                    current_state=rec.get("current_state", ""),
                    recommended_next_step=rec.get("recommended_next_step", ""),
                    practical_action=rec.get("practical_action", ""),
                    evidence=rec.get("evidence", ""),
                    generated_by=rec.get("generated_by", "rule")
                ))

        search_run.status = "completed"
        search_run.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(analysis)

        return analysis


market_analysis_service = MarketAnalysisService()
