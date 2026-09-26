from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, CandidateProfile, CandidateSkill, Skill, Role
from app.schemas.profile import ProfileResponse, ProfileUpdate, CandidateSkillInput, CandidateSkillResponse
from app.services.skill_progress_service import skill_progress_service

router = APIRouter(prefix="/profile", tags=["Candidate Profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    candidate_skills = db.query(CandidateSkill).filter(CandidateSkill.user_id == current_user.id).all()
    skills_response = []
    for cs in candidate_skills:
        skills_response.append(CandidateSkillResponse(
            id=cs.id,
            skill_id=cs.skill_id,
            name=cs.skill.name if cs.skill else "Skill",
            category=cs.skill.category if cs.skill else "General",
            proficiency=cs.proficiency,
            confidence=cs.confidence,
            years_experience=cs.years_experience
        ))

    return ProfileResponse(
        id=profile.id,
        user_id=current_user.id,
        target_role=profile.role.name if profile.role else None,
        target_location=profile.target_location,
        remote_preference=profile.remote_preference or "flexible",
        experience_years=profile.experience_years or 0,
        skills=skills_response
    )


@router.put("", response_model=ProfileResponse)
def update_profile(profile_in: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)

    if profile_in.target_role_name:
        role = db.query(Role).filter(Role.normalized_name == profile_in.target_role_name.lower()).first()
        if not role:
            role = Role(name=profile_in.target_role_name.title(), normalized_name=profile_in.target_role_name.lower())
            db.add(role)
            db.flush()
        profile.target_role_id = role.id

    if profile_in.target_location is not None:
        profile.target_location = profile_in.target_location
    if profile_in.remote_preference is not None:
        profile.remote_preference = profile_in.remote_preference
    if profile_in.experience_years is not None:
        profile.experience_years = profile_in.experience_years

    # Track prior skills for progress timeline
    existing_skills_map = {
        cs.skill_id: cs.proficiency
        for cs in db.query(CandidateSkill).filter(CandidateSkill.user_id == current_user.id).all()
    }

    # Update skills if provided
    if profile_in.skills is not None:
        db.query(CandidateSkill).filter(CandidateSkill.user_id == current_user.id).delete()
        for sk_input in profile_in.skills:
            norm_name = sk_input.name.strip().lower()
            canonical_skill = db.query(Skill).filter(Skill.normalized_name == norm_name).first()
            if not canonical_skill:
                canonical_skill = Skill(name=sk_input.name.strip(), normalized_name=norm_name)
                db.add(canonical_skill)
                db.flush()

            prev_prof = existing_skills_map.get(canonical_skill.id)
            if prev_prof != sk_input.proficiency:
                skill_progress_service.record_skill_change(
                    db=db,
                    user_id=current_user.id,
                    skill_id=canonical_skill.id,
                    from_proficiency=prev_prof,
                    to_proficiency=sk_input.proficiency
                )

            db.add(CandidateSkill(
                user_id=current_user.id,
                skill_id=canonical_skill.id,
                proficiency=sk_input.proficiency,
                years_experience=sk_input.years_experience or 1.0
            ))

    db.commit()
    return get_profile(current_user=current_user, db=db)


@router.get("/progress")
def get_skill_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieve candidate's chronological skill evolution timeline.
    """
    return skill_progress_service.get_candidate_skill_timeline(db=db, user_id=current_user.id)
