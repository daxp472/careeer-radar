from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, CandidateJobAlertSettings, CandidateJobScan
from app.services.candidate_scan_service import candidate_scan_service

router = APIRouter(prefix="/automation", tags=["Candidate Automated Radar Scans"])


class AlertSettingsUpdate(BaseModel):
    enabled: Optional[bool] = None
    frequency: Optional[str] = "weekly"
    day_of_week: Optional[str] = "monday"
    time_of_day: Optional[str] = "10:00"
    timezone: Optional[str] = "Asia/Kolkata"
    minimum_match_score: Optional[float] = 80.0
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None


class AlertSettingsResponse(BaseModel):
    id: str
    user_id: str
    enabled: bool
    frequency: str
    day_of_week: str
    time_of_day: str
    timezone: str
    minimum_match_score: float
    email_enabled: bool
    in_app_enabled: bool
    last_scan_at: Optional[datetime] = None
    next_scan_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CandidateScanHistoryItem(BaseModel):
    id: str
    started_at: datetime
    completed_at: Optional[datetime]
    jobs_checked: int
    jobs_matched: int
    jobs_above_threshold: int
    email_sent: bool
    status: str
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


@router.get("/settings", response_model=AlertSettingsResponse)
def get_alert_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return candidate_scan_service.get_or_create_alert_settings(db, current_user.id)


@router.put("/settings", response_model=AlertSettingsResponse)
def update_alert_settings(
    settings_in: AlertSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = candidate_scan_service.get_or_create_alert_settings(db, current_user.id)

    if settings_in.enabled is not None:
        settings.enabled = settings_in.enabled
    if settings_in.frequency is not None:
        settings.frequency = settings_in.frequency
    if settings_in.day_of_week is not None:
        settings.day_of_week = settings_in.day_of_week.lower()
    if settings_in.time_of_day is not None:
        settings.time_of_day = settings_in.time_of_day
    if settings_in.timezone is not None:
        settings.timezone = settings_in.timezone
    if settings_in.minimum_match_score is not None:
        settings.minimum_match_score = settings_in.minimum_match_score
    if settings_in.email_enabled is not None:
        settings.email_enabled = settings_in.email_enabled
    if settings_in.in_app_enabled is not None:
        settings.in_app_enabled = settings_in.in_app_enabled

    # Recalculate next scan time
    settings.next_scan_at = candidate_scan_service.calculate_next_scan_at(
        day_of_week=settings.day_of_week,
        time_of_day=settings.time_of_day,
        timezone_str=settings.timezone
    )

    db.commit()
    db.refresh(settings)
    return settings


@router.post("/scan-now")
def scan_now(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Manually trigger candidate scan against latest CareerRadar database immediately.
    """
    scan_record = candidate_scan_service.execute_candidate_scan(db=db, user_id=current_user.id, is_manual=True)
    return {
        "message": "Candidate scan completed successfully.",
        "scan_id": scan_record.id,
        "status": scan_record.status,
        "jobs_checked": scan_record.jobs_checked,
        "jobs_above_threshold": scan_record.jobs_above_threshold,
        "email_sent": scan_record.email_sent
    }


@router.get("/scans", response_model=List[CandidateScanHistoryItem])
def get_scan_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scans = db.query(CandidateJobScan).filter(
        CandidateJobScan.user_id == current_user.id
    ).order_by(CandidateJobScan.started_at.desc()).limit(20).all()
    return scans
