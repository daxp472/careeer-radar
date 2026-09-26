from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.services.watchlist_service import watchlist_service

router = APIRouter(prefix="/watchlist", tags=["Candidate Watchlist"])


class WatchlistAddRequest(BaseModel):
    notes: Optional[str] = None


@router.post("/{job_id}", status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    job_id: str,
    req: Optional[WatchlistAddRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notes = req.notes if req else None
    item = watchlist_service.add_to_watchlist(db=db, user_id=current_user.id, job_id=job_id, notes=notes)
    return {"message": "Job added to watchlist.", "watchlist_id": item.id}


@router.delete("/{job_id}")
def remove_from_watchlist(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = watchlist_service.remove_from_watchlist(db=db, user_id=current_user.id, job_id=job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Watchlist entry not found.")
    return {"message": "Job removed from watchlist."}


@router.get("")
def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get saved jobs for candidate with dynamically recalculated match scores and current job status.
    """
    return watchlist_service.get_user_watchlist_with_matches(db=db, user_id=current_user.id)
