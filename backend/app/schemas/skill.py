from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SkillSchema(BaseModel):
    id: str
    name: str
    normalized_name: str
    category: Optional[str] = "General"
    aliases: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class RoleSchema(BaseModel):
    id: str
    name: str
    normalized_name: str

    model_config = ConfigDict(from_attributes=True)
