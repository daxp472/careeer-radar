from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Skill, Role
from app.schemas.skill import SkillSchema, RoleSchema

router = APIRouter(tags=["Skills & Roles"])


@router.get("/roles", response_model=List[RoleSchema])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).order_by(Role.name).all()


@router.get("/skills", response_model=List[SkillSchema])
def list_skills(
    category: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    return query.order_by(Skill.name).limit(limit).all()


@router.get("/skills/search", response_model=List[SkillSchema])
def search_skills(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    term = f"%{q.lower()}%"
    return db.query(Skill).filter(
        (Skill.normalized_name.ilike(term)) | (Skill.name.ilike(term))
    ).limit(20).all()
