from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import (
    ReadinessAnalysis, ReadinessGap, MarketSnapshot, MarketSkillStat,
    JobCandidateAnalysis, Skill, CandidateSkill, User
)
from app.schemas.analysis import (
    WhatChangedResponse, SkillChangeItem,
    CandidateFeedbackReportResponse, CandidateFeedbackSection,
    MarketRecommendationItem
)
from app.services.recommendation_service import recommendation_service


class ProgressIntelligenceService:
    @classmethod
    def compare_analyses(
        cls,
        db: Session,
        current_analysis_id: str,
        previous_analysis_id: Optional[str] = None
    ) -> WhatChangedResponse:
        """
        Deterministic comparison between current analysis and its previous historical baseline.
        Identifies readiness score delta, newly acquired skills, improved proficiencies,
        removed gaps, and market requirement shifts.
        """
        curr = db.query(ReadinessAnalysis).filter(ReadinessAnalysis.id == current_analysis_id).first()
        if not curr:
            raise ValueError("Current analysis record not found.")

        # Find previous analysis if not explicitly provided
        prev = None
        if previous_analysis_id:
            prev = db.query(ReadinessAnalysis).filter(ReadinessAnalysis.id == previous_analysis_id).first()
        elif curr.user_id:
            prev = db.query(ReadinessAnalysis).filter(
                ReadinessAnalysis.user_id == curr.user_id,
                ReadinessAnalysis.created_at < curr.created_at
            ).order_by(ReadinessAnalysis.created_at.desc()).first()

        curr_snapshot = curr.snapshot
        curr_jobs_count = curr_snapshot.jobs_analyzed if curr_snapshot else 0
        curr_score = round(curr.readiness_score, 1)

        if not prev:
            # Baseline analysis
            summary = (
                f"This is your baseline market readiness scan for {curr_snapshot.role.name if curr_snapshot and curr_snapshot.role else 'this role'}. "
                f"You achieved an initial readiness score of {curr_score}%. Subsequent analyses will track your growth delta and gap reduction."
            )
            return WhatChangedResponse(
                has_previous_analysis=False,
                current_analysis_id=curr.id,
                previous_analysis_id=None,
                current_created_at=curr.created_at,
                previous_created_at=None,
                current_readiness_score=curr_score,
                previous_readiness_score=None,
                readiness_score_change=0.0,
                current_jobs_count=curr_jobs_count,
                previous_jobs_count=None,
                newly_acquired_skills=[],
                improved_proficiencies=[],
                weakened_skills=[],
                removed_gaps=[],
                new_gaps=[],
                jobs_above_threshold_change=0,
                market_priority_shifts=[],
                summary=summary
            )

        prev_snapshot = prev.snapshot
        prev_jobs_count = prev_snapshot.jobs_analyzed if prev_snapshot else 0
        prev_score = round(prev.readiness_score, 1)
        score_change = round(curr_score - prev_score, 1)

        # Compare Gaps & Skills
        curr_gaps = db.query(ReadinessGap).filter(ReadinessGap.analysis_id == curr.id).all()
        prev_gaps = db.query(ReadinessGap).filter(ReadinessGap.analysis_id == prev.id).all()

        curr_gap_map = {g.skill_id: g for g in curr_gaps}
        prev_gap_map = {g.skill_id: g for g in prev_gaps}

        proficiency_rank = {"beginner": 1, "known": 2, "intermediate": 3, "advanced": 4, "expert": 5}

        newly_acquired = []
        improved = []
        weakened = []
        removed_gaps = []
        new_gaps = []

        all_skill_ids = set(curr_gap_map.keys()).union(set(prev_gap_map.keys()))

        for sk_id in all_skill_ids:
            cg = curr_gap_map.get(sk_id)
            pg = prev_gap_map.get(sk_id)

            sk_name = (cg.skill.name if cg and cg.skill else (pg.skill.name if pg and pg.skill else "Skill"))
            sk_cat = (cg.skill.category if cg and cg.skill else (pg.skill.category if pg and pg.skill else "General"))
            freq = cg.market_frequency_pct if cg else (pg.market_frequency_pct if pg else 0.0)

            # Check for proficiency change (improved or weakened)
            if pg and cg and pg.candidate_proficiency and cg.candidate_proficiency:
                p_rank = proficiency_rank.get(pg.candidate_proficiency.lower(), 0)
                c_rank = proficiency_rank.get(cg.candidate_proficiency.lower(), 0)
                if c_rank > p_rank:
                    improved.append(SkillChangeItem(
                        skill_name=sk_name,
                        category=sk_cat,
                        from_proficiency=pg.candidate_proficiency,
                        to_proficiency=cg.candidate_proficiency,
                        change_type="improved",
                        market_frequency_pct=freq
                    ))
                elif c_rank < p_rank:
                    weakened.append(SkillChangeItem(
                        skill_name=sk_name,
                        category=sk_cat,
                        from_proficiency=pg.candidate_proficiency,
                        to_proficiency=cg.candidate_proficiency,
                        change_type="weakened",
                        market_frequency_pct=freq
                    ))

            # Case: Was missing/weak, now matched
            if pg and pg.gap_type in ["missing", "weak"] and cg and cg.gap_type == "matched":
                newly_acquired.append(SkillChangeItem(
                    skill_name=sk_name,
                    category=sk_cat,
                    from_proficiency=pg.candidate_proficiency or "missing",
                    to_proficiency=cg.candidate_proficiency or "known",
                    change_type="acquired",
                    market_frequency_pct=freq
                ))
                removed_gaps.append(SkillChangeItem(
                    skill_name=sk_name,
                    category=sk_cat,
                    from_proficiency=pg.candidate_proficiency or "missing",
                    to_proficiency=cg.candidate_proficiency or "known",
                    change_type="removed_gap",
                    market_frequency_pct=freq
                ))

            # Case: New gap
            elif (not pg or pg.gap_type == "matched") and (cg and cg.gap_type in ["missing", "weak"]):
                new_gaps.append(SkillChangeItem(
                    skill_name=sk_name,
                    category=sk_cat,
                    from_proficiency=pg.candidate_proficiency if pg else None,
                    to_proficiency=cg.candidate_proficiency or "missing",
                    change_type="new_gap",
                    market_frequency_pct=freq
                ))

        # Job matching change
        curr_high_matches = db.query(JobCandidateAnalysis).filter(
            JobCandidateAnalysis.readiness_analysis_id == curr.id,
            JobCandidateAnalysis.match_score >= 80.0
        ).count()
        prev_high_matches = db.query(JobCandidateAnalysis).filter(
            JobCandidateAnalysis.readiness_analysis_id == prev.id,
            JobCandidateAnalysis.match_score >= 80.0
        ).count()
        job_match_change = curr_high_matches - prev_high_matches

        # Market Priority Shifts
        curr_stats = db.query(MarketSkillStat).filter(MarketSkillStat.snapshot_id == curr_snapshot.id).all() if curr_snapshot else []
        prev_stats = db.query(MarketSkillStat).filter(MarketSkillStat.snapshot_id == prev_snapshot.id).all() if prev_snapshot else []
        prev_stat_map = {ps.skill_id: ps.frequency_pct for ps in prev_stats}
        shifts = []
        for cs in curr_stats:
            old_freq = prev_stat_map.get(cs.skill_id)
            if old_freq is not None and abs(cs.frequency_pct - old_freq) >= 10.0:
                sk = cs.skill
                shifts.append({
                    "skill_name": sk.name if sk else "Skill",
                    "previous_frequency_pct": old_freq,
                    "current_frequency_pct": cs.frequency_pct,
                    "delta_pct": round(cs.frequency_pct - old_freq, 1)
                })

        # Construct deterministic fact-based summary
        summary_parts = []
        if score_change > 0:
            summary_parts.append(f"Your market readiness increased by +{score_change}% (from {prev_score}% to {curr_score}%).")
        elif score_change < 0:
            summary_parts.append(f"Your market readiness shifted by {score_change}% (from {prev_score}% to {curr_score}%) due to higher market demand for unverified skills.")
        else:
            summary_parts.append(f"Your market readiness remained steady at {curr_score}%.")

        if removed_gaps:
            gap_names = ", ".join([rg.skill_name for rg in removed_gaps[:3]])
            summary_parts.append(f"You successfully eliminated market gaps in: {gap_names}.")

        if improved:
            imp_names = ", ".join([f"{imp.skill_name} ({imp.from_proficiency} → {imp.to_proficiency})" for imp in improved[:3]])
            summary_parts.append(f"Verified skill upgrades: {imp_names}.")

        if job_match_change > 0:
            summary_parts.append(f"{job_match_change} more analyzed opportunities now match your profile at 80%+.")

        return WhatChangedResponse(
            has_previous_analysis=True,
            current_analysis_id=curr.id,
            previous_analysis_id=prev.id,
            current_created_at=curr.created_at,
            previous_created_at=prev.created_at,
            current_readiness_score=curr_score,
            previous_readiness_score=prev_score,
            readiness_score_change=score_change,
            current_jobs_count=curr_jobs_count,
            previous_jobs_count=prev_jobs_count,
            newly_acquired_skills=newly_acquired,
            improved_proficiencies=improved,
            weakened_skills=weakened,
            removed_gaps=removed_gaps,
            new_gaps=new_gaps,
            jobs_above_threshold_change=job_match_change,
            market_priority_shifts=shifts,
            summary=" ".join(summary_parts)
        )

    @classmethod
    def get_candidate_feedback_report(cls, db: Session, analysis_id: str) -> CandidateFeedbackReportResponse:
        """
        Assemble the complete structured candidate intelligence report.
        """
        analysis = db.query(ReadinessAnalysis).filter(ReadinessAnalysis.id == analysis_id).first()
        if not analysis:
            raise ValueError("Analysis not found.")

        snapshot = analysis.snapshot
        role_name = snapshot.role.name if snapshot and snapshot.role else "Software Developer"
        location = snapshot.location if snapshot else "Global"
        score = round(analysis.readiness_score, 1)

        # Determine Tier
        if score >= 85.0:
            tier = "Highly Ready"
        elif score >= 70.0:
            tier = "Strong Alignment"
        elif score >= 50.0:
            tier = "Building Foundation"
        else:
            tier = "Early Stage"

        # What Changed
        what_changed = cls.compare_analyses(db=db, current_analysis_id=analysis_id)

        # Gaps
        gaps = db.query(ReadinessGap).filter(ReadinessGap.analysis_id == analysis.id).all()
        matched = [g for g in gaps if g.gap_type == "matched"]
        missing = [g for g in gaps if g.gap_type == "missing"]
        weak = [g for g in gaps if g.gap_type == "weak"]

        matched.sort(key=lambda x: x.market_frequency_pct, reverse=True)
        missing.sort(key=lambda x: x.priority_score, reverse=True)
        weak.sort(key=lambda x: x.priority_score, reverse=True)

        # 1. Current Position
        current_pos = CandidateFeedbackSection(
            title="Current Market Standing",
            badge=tier,
            summary=f"You match {score}% of the core technical requirements across {snapshot.jobs_analyzed if snapshot else 0} live {role_name} opportunities in {location}.",
            items=[
                {"metric": "Readiness Score", "value": f"{score}%"},
                {"metric": "Target Market", "value": f"{role_name} ({location})"},
                {"metric": "Jobs Analyzed", "value": snapshot.jobs_analyzed if snapshot else 0},
                {"metric": "Market Standing", "value": tier}
            ]
        )

        # 2. Strongest Areas
        strong_items = [
            {
                "skill": g.skill.name if g.skill else "Skill",
                "category": g.skill.category if g.skill else "General",
                "proficiency": g.candidate_proficiency or "known",
                "market_frequency_pct": g.market_frequency_pct,
                "note": f"Present in {g.market_frequency_pct}% of live jobs"
            }
            for g in matched[:6]
        ]
        strongest_areas = CandidateFeedbackSection(
            title="Your Strongest Areas",
            badge=f"{len(matched)} Matched Skills",
            summary=f"You have verified market coverage across {len(matched)} key requirements requested by employers.",
            items=strong_items
        )

        # 3. Biggest Gaps
        gap_items = []
        for g in missing[:5]:
            gap_items.append({
                "skill": g.skill.name if g.skill else "Skill",
                "category": g.skill.category if g.skill else "General",
                "type": "Missing Requirement",
                "market_frequency_pct": g.market_frequency_pct,
                "priority_score": g.priority_score,
                "note": f"Required in {g.market_frequency_pct}% of opportunities"
            })
        for g in weak[:3]:
            gap_items.append({
                "skill": g.skill.name if g.skill else "Skill",
                "category": g.skill.category if g.skill else "General",
                "type": "Depth Upgrade Needed",
                "market_frequency_pct": g.market_frequency_pct,
                "priority_score": g.priority_score,
                "note": f"Current proficiency ({g.candidate_proficiency}) below market expectation"
            })

        biggest_gaps = CandidateFeedbackSection(
            title="Top Skill Gaps to Bridge",
            badge=f"{len(missing) + len(weak)} Open Gaps",
            summary="Focusing on these top market gaps will give you the highest immediate ROI in job match percentage.",
            items=gap_items
        )

        # 4. Market Signals
        market_stats = db.query(MarketSkillStat).filter(MarketSkillStat.snapshot_id == snapshot.id).order_by(MarketSkillStat.frequency_pct.desc()).limit(8).all() if snapshot else []
        signal_items = [
            {
                "skill": ms.skill.name if ms.skill else "Skill",
                "frequency_pct": ms.frequency_pct,
                "jobs_with_skill": ms.jobs_with_skill,
                "candidate_status": "matched" if any(m.skill_id == ms.skill_id for m in matched) else "missing"
            }
            for ms in market_stats
        ]
        market_signals = CandidateFeedbackSection(
            title="Live Market Demand Signals",
            badge=f"{len(market_stats)} Core Skills Tracked",
            summary=f"Empirical requirement distribution observed across {snapshot.jobs_analyzed if snapshot else 0} live job postings.",
            items=signal_items
        )

        # 5. Action Plan with Bridges
        candidate_known = [m.skill.name for m in matched if m.skill]
        action_plan_raw = recommendation_service.generate_market_recommendations(
            market_stats=[{"name": ms.skill.name, "frequency_pct": ms.frequency_pct, "jobs_with_skill": ms.jobs_with_skill} for ms in market_stats if ms.skill],
            gaps=[{"skill_id": g.skill_id, "name": g.skill.name if g.skill else "Skill", "gap_type": g.gap_type, "market_frequency_pct": g.market_frequency_pct, "importance_score": g.importance_score} for g in gaps],
            job_analyses=[],
            candidate_skills=[{"name": k} for k in candidate_known]
        )

        action_items = [
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
                total_jobs_analyzed=r.get("total_jobs_analyzed", snapshot.jobs_analyzed if snapshot else 0)
            )
            for r in action_plan_raw
        ]

        return CandidateFeedbackReportResponse(
            analysis_id=analysis.id,
            target_role=role_name,
            location=location,
            readiness_score=score,
            alignment_tier=tier,
            analyzed_at=analysis.created_at,
            current_position=current_pos,
            strongest_areas=strongest_areas,
            biggest_gaps=biggest_gaps,
            what_changed=what_changed,
            market_signals=market_signals,
            personalized_action_plan=action_items
        )


progress_intelligence_service = ProgressIntelligenceService()
