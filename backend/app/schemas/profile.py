from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SkillBase(BaseModel):
    id: str
    name: str
    normalized_name: str
    category: Optional[str] = "General"
    aliases: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class CandidateSkillInput(BaseModel):
    name: str  # e.g., "React"
    proficiency: str = "known"  # beginner, known, intermediate, advanced, expert
    years_experience: Optional[float] = 1.0


class CandidateSkillResponse(BaseModel):
    id: str
    skill_id: str
    name: str
    category: Optional[str]
    proficiency: str
    confidence: float
    years_experience: float

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    target_role_name: Optional[str] = None
    target_location: Optional[str] = None
    remote_preference: Optional[str] = "flexible"
    experience_years: Optional[int] = 0
    skills: Optional[List[CandidateSkillInput]] = []


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    target_role: Optional[str] = None
    target_location: Optional[str] = None
    remote_preference: str = "flexible"
    experience_years: int = 0
    skills: List[CandidateSkillResponse] = []

    model_config = ConfigDict(from_attributes=True)
