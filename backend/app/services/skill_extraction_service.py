import re
from typing import List, Dict, Set, Tuple
from sqlalchemy.orm import Session
from app.models import Skill, JobSkill


class SkillExtractionService:
    @staticmethod
    def extract_skills_from_text(text: str, canonical_skills: List[Skill]) -> List[Tuple[Skill, int, str]]:
        """
        Extract canonical skills from job title and description text.
        Returns list of tuples: (Skill, mention_count, extraction_method)
        """
        if not text:
            return []

        lower_text = text.lower()
        extracted: Dict[str, Tuple[Skill, int, str]] = {}

        for skill in canonical_skills:
            all_patterns: Set[str] = {skill.normalized_name}
            if skill.aliases:
                for alias in skill.aliases:
                    if isinstance(alias, str):
                        all_patterns.add(alias.lower())

            total_mentions = 0
            for pattern in all_patterns:
                # Regex word boundary matching (escaping special characters like c#, c++)
                escaped_pattern = re.escape(pattern)
                # Word boundaries for alphanumeric or boundary for symbols
                regex = rf"(?:\b|(?<=\s)){escaped_pattern}(?=\b|[\s,.;:!?)]|$)"
                matches = re.findall(regex, lower_text)
                if matches:
                    total_mentions += len(matches)

            if total_mentions > 0:
                extracted[skill.id] = (skill, total_mentions, "rule")

        return list(extracted.values())


skill_extraction_service = SkillExtractionService()
