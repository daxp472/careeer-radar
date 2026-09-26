from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import SkillProgressHistory, Skill, CandidateSkill


class SkillProgressService:
    @classmethod
    def record_skill_change(
        cls,
        db: Session,
        user_id: str,
        skill_id: str,
        from_proficiency: Optional[str],
        to_proficiency: str
    ) -> Optional[SkillProgressHistory]:
        if from_proficiency == to_proficiency:
            return None

        history_item = SkillProgressHistory(
            user_id=user_id,
            skill_id=skill_id,
            from_proficiency=from_proficiency,
            to_proficiency=to_proficiency,
            recorded_at=datetime.utcnow()
        )
        db.add(history_item)
        db.commit()
        return history_item

    @classmethod
    def get_candidate_skill_timeline(cls, db: Session, user_id: str) -> List[Dict[str, Any]]:
        history_records = db.query(SkillProgressHistory).filter(
            SkillProgressHistory.user_id == user_id
        ).order_by(SkillProgressHistory.recorded_at.desc()).all()

        results = []
        for h in history_records:
            sk = h.skill
            results.append({
                "id": h.id,
                "skill_id": h.skill_id,
                "skill_name": sk.name if sk else "Skill",
                "category": sk.category if sk else "General",
                "from_proficiency": h.from_proficiency or "missing",
                "to_proficiency": h.to_proficiency,
                "recorded_at": h.recorded_at
            })
        return results


skill_progress_service = SkillProgressService()
