from typing import List, Dict, Any, Optional
from app.core.logging import logger

PROFICIENCY_COVERAGE_MAP = {
    "beginner": 0.25,
    "known": 0.50,
    "intermediate": 0.70,
    "advanced": 0.90,
    "expert": 1.00,
}


class ReadinessService:
    @staticmethod
    def calculate_readiness_score(
        market_stats: List[Dict[str, Any]], 
        candidate_skills_dict: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        DETERMINISTIC READINESS ENGINE
        
        Formula:
            Readiness = [ SUM( market_importance_i * candidate_coverage_i ) / SUM( market_importance_i ) ] * 100
            
        Where:
            market_importance_i = frequency_pct_i
            candidate_coverage_i:
                beginner     = 0.25
                known        = 0.50
                intermediate = 0.70
                advanced     = 0.90
                expert       = 1.00
                missing      = 0.00
        """
        if not market_stats:
            return {
                "readiness_score": 0.0,
                "gaps": [],
                "matched": [],
                "weak": [],
                "missing": []
            }

        total_market_importance = 0.0
        covered_market_importance = 0.0

        all_gaps = []
        matched_gaps = []
        weak_gaps = []
        missing_gaps = []

        for stat in market_stats:
            skill_id = stat["skill_id"]
            skill_name = stat["name"]
            category = stat.get("category", "General")
            frequency_pct = stat["frequency_pct"]
            importance_score = stat.get("market_importance_score", frequency_pct)

            total_market_importance += importance_score

            candidate_skill = candidate_skills_dict.get(skill_id) or candidate_skills_dict.get(skill_name.lower())
            
            if candidate_skill:
                proficiency = candidate_skill.get("proficiency", "known").lower()
                coverage = PROFICIENCY_COVERAGE_MAP.get(proficiency, 0.50)
            else:
                proficiency = None
                coverage = 0.0

            covered_market_importance += (importance_score * coverage)

            # Priority score: High market frequency + large candidate deficit
            priority_score = round(frequency_pct * (1.0 - coverage), 2)

            gap_item = {
                "skill_id": skill_id,
                "name": skill_name,
                "category": category,
                "market_frequency_pct": round(frequency_pct, 1),
                "importance_score": round(importance_score, 2),
                "candidate_proficiency": proficiency,
                "priority_score": priority_score,
                "coverage": coverage
            }

            if coverage >= 0.70:
                gap_item["gap_type"] = "matched"
                gap_item["explanation"] = f"Strong match: You have {proficiency} proficiency for a skill appearing in {round(frequency_pct)}% of jobs."
                matched_gaps.append(gap_item)
            elif coverage > 0.0:
                gap_item["gap_type"] = "weak"
                gap_item["explanation"] = f"Weak match: Your {proficiency} level leaves an opportunity to level up in this skill ({round(frequency_pct)}% of jobs)."
                weak_gaps.append(gap_item)
            else:
                gap_item["gap_type"] = "missing"
                gap_item["explanation"] = f"Missing high-demand skill: Appears in {round(frequency_pct)}% of analyzed jobs."
                missing_gaps.append(gap_item)

            all_gaps.append(gap_item)

        # Calculate final deterministic percentage
        if total_market_importance > 0:
            raw_score = (covered_market_importance / total_market_importance) * 100.0
            readiness_score = round(min(100.0, max(0.0, raw_score)), 1)
        else:
            readiness_score = 0.0

        # Sort gaps by priority score descending
        all_gaps.sort(key=lambda x: x["priority_score"], reverse=True)
        missing_gaps.sort(key=lambda x: x["priority_score"], reverse=True)
        weak_gaps.sort(key=lambda x: x["priority_score"], reverse=True)
        matched_gaps.sort(key=lambda x: x["market_frequency_pct"], reverse=True)

        return {
            "readiness_score": readiness_score,
            "gaps": all_gaps,
            "matched": matched_gaps,
            "weak": weak_gaps,
            "missing": missing_gaps
        }


readiness_service = ReadinessService()
