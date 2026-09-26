from typing import List, Dict, Any, Optional, Set
from app.models import Job, Skill, JobSkill, CandidateSkill
from app.core.logging import logger

PROFICIENCY_COVERAGE_MAP = {
    "beginner": 0.25,
    "known": 0.50,
    "intermediate": 0.70,
    "advanced": 0.90,
    "expert": 1.00,
}

IMPORTANCE_WEIGHT_MAP = {
    "required": 3.0,
    "preferred": 1.5,
    "mentioned": 1.0,
}


class JobMatchService:
    @staticmethod
    def build_candidate_skill_lookup(
        candidate_skills: List[Dict[str, Any]],
        canonical_skills: List[Skill]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Build a dictionary mapping canonical skill IDs to candidate proficiency details,
        handling alias resolution so 'Amazon Web Services' -> 'AWS', 'TS' -> 'TypeScript', etc.
        """
        lookup: Dict[str, Dict[str, Any]] = {}

        # Create alias map
        alias_to_canonical: Dict[str, Skill] = {}
        for skill in canonical_skills:
            alias_to_canonical[skill.normalized_name] = skill
            alias_to_canonical[skill.name.lower()] = skill
            if skill.aliases:
                for alias in skill.aliases:
                    if isinstance(alias, str):
                        alias_to_canonical[alias.lower().strip()] = skill

        for c_skill in candidate_skills:
            raw_name = c_skill.get("name", "").strip().lower()
            if not raw_name:
                continue

            canonical = alias_to_canonical.get(raw_name)
            skill_id = canonical.id if canonical else raw_name
            canonical_name = canonical.name if canonical else c_skill.get("name")
            
            proficiency = str(c_skill.get("proficiency", "known")).lower()
            coverage = PROFICIENCY_COVERAGE_MAP.get(proficiency, 0.50)

            lookup[skill_id] = {
                "skill_id": skill_id,
                "name": canonical_name,
                "proficiency": proficiency,
                "coverage": coverage,
                "years_experience": float(c_skill.get("years_experience", 1.0))
            }

        return lookup

    @classmethod
    def analyze_job_for_candidate(
        cls,
        job_id: str,
        job_skills: List[JobSkill],
        candidate_lookup: Dict[str, Dict[str, Any]],
        market_frequencies: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Perform deterministic Job-Level Skill Gap Analysis.
        Returns match scores, required/preferred skill breakdowns, classified gaps with evidence, and priorities.
        """
        market_freq = market_frequencies or {}

        total_weight = 0.0
        covered_weight = 0.0

        required_total_weight = 0.0
        required_covered_weight = 0.0

        preferred_total_weight = 0.0
        preferred_covered_weight = 0.0

        gaps = []
        matched_skills = []
        weak_skills = []
        missing_skills = []

        total_required = 0
        matched_required = 0
        missing_required = 0
        weak_required = 0

        total_preferred = 0
        matched_preferred = 0
        missing_preferred = 0
        weak_preferred = 0

        for js in job_skills:
            skill = js.skill
            if not skill:
                continue

            skill_id = skill.id
            skill_name = skill.name
            importance = js.importance or "required"
            imp_weight = IMPORTANCE_WEIGHT_MAP.get(importance, 1.0)

            total_weight += imp_weight
            if importance == "required":
                required_total_weight += imp_weight
                total_required += 1
            elif importance == "preferred":
                preferred_total_weight += imp_weight
                total_preferred += 1

            # Check candidate match
            c_skill = candidate_lookup.get(skill_id)
            if c_skill:
                coverage = c_skill.get("coverage", PROFICIENCY_COVERAGE_MAP.get(c_skill.get("proficiency", "known").lower(), 0.50))
                proficiency = c_skill.get("proficiency", "known")
            else:
                coverage = 0.0
                proficiency = None

            covered_weight += (imp_weight * coverage)
            if importance == "required":
                required_covered_weight += (imp_weight * coverage)
            elif importance == "preferred":
                preferred_covered_weight += (imp_weight * coverage)

            freq_pct = market_freq.get(skill_id, market_freq.get(skill_name.lower(), 50.0))

            # Classification
            if coverage >= 0.70 or (importance == "preferred" and coverage >= 0.50):
                gap_type = "matched"
                evidence = f"{skill_name} is a {importance} skill for this job. You have {proficiency} proficiency."
                matched_skills.append({
                    "skill_id": skill_id,
                    "name": skill_name,
                    "importance": importance,
                    "proficiency": proficiency,
                    "coverage": coverage
                })
                if importance == "required":
                    matched_required += 1
                elif importance == "preferred":
                    matched_preferred += 1
            elif coverage > 0.0:
                gap_type = "weak"
                evidence = f"{skill_name} is listed as a {importance} skill for this job. Your current proficiency is {proficiency}, creating a depth gap."
                weak_skills.append({
                    "skill_id": skill_id,
                    "name": skill_name,
                    "importance": importance,
                    "proficiency": proficiency,
                    "coverage": coverage
                })
                if importance == "required":
                    weak_required += 1
                elif importance == "preferred":
                    weak_preferred += 1
            else:
                gap_type = "missing"
                evidence = f"{skill_name} is a {importance} skill for this position, but is not currently present in your candidate profile."
                missing_skills.append({
                    "skill_id": skill_id,
                    "name": skill_name,
                    "importance": importance,
                    "proficiency": None,
                    "coverage": 0.0
                })
                if importance == "required":
                    missing_required += 1
                elif importance == "preferred":
                    missing_preferred += 1

            # Calculate Job Gap Priority
            # Required + Missing has highest priority
            priority_score = round(
                imp_weight * 10.0 * (1.0 - coverage) * (1.0 + (freq_pct / 100.0)),
                2
            )

            gaps.append({
                "skill_id": skill_id,
                "name": skill_name,
                "category": skill.category or "General",
                "gap_type": gap_type,
                "job_importance": importance,
                "candidate_proficiency": proficiency,
                "priority_score": priority_score,
                "evidence": evidence,
                "market_frequency_pct": freq_pct
            })

        # Calculate Overall Match Score
        if total_weight > 0:
            match_score = round((covered_weight / total_weight) * 100.0, 1)
        else:
            match_score = 100.0 if len(job_skills) == 0 else 0.0

        # Calculate Required Match Score
        if required_total_weight > 0:
            required_match_score = round((required_covered_weight / required_total_weight) * 100.0, 1)
        else:
            required_match_score = 100.0

        # Calculate Preferred Match Score
        if preferred_total_weight > 0:
            preferred_match_score = round((preferred_covered_weight / preferred_total_weight) * 100.0, 1)
        else:
            preferred_match_score = 100.0

        # Sort gaps by priority descending
        gaps.sort(key=lambda x: x["priority_score"], reverse=True)

        return {
            "job_id": job_id,
            "match_score": match_score,
            "required_match_score": required_match_score,
            "preferred_match_score": preferred_match_score,
            "total_skills": len(job_skills),
            "total_required_skills": total_required,
            "matched_required_skills": matched_required,
            "missing_required_skills": missing_required,
            "weak_required_skills": weak_required,
            "total_preferred_skills": total_preferred,
            "matched_preferred_skills": matched_preferred,
            "missing_preferred_skills": missing_preferred,
            "weak_preferred_skills": weak_preferred,
            "matched_skills": matched_skills,
            "weak_skills": weak_skills,
            "missing_skills": missing_skills,
            "gaps": gaps
        }


job_match_service = JobMatchService()
