from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.application import Application
from app.models.followup import FollowUp
from app.models.user import User
from app.schemas.followup import FollowUpCreate, FollowUpOut

router = APIRouter()


@router.get("/", response_model=list[FollowUpOut])
def list_followups(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # verify that the application belongs to the current user
    app_obj = (
        db.query(Application)
        .filter(Application.id == application_id, Application.owner_id == user.id)
        .first()
    )
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    return (
        db.query(FollowUp)
        .filter(
            FollowUp.application_id == application_id,
            FollowUp.owner_id == user.id,
        )
        .order_by(FollowUp.id.desc())
        .all()
    )


@router.post("/", response_model=FollowUpOut, status_code=201)
def create_followup(
    payload: FollowUpCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # ensure the user owns the application
    app_obj = (
        db.query(Application)
        .filter(
            Application.id == payload.application_id,
            Application.owner_id == user.id,
        )
        .first()
    )
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    fu = FollowUp(
        note=payload.note,
        application_id=payload.application_id,
        owner_id=user.id,
    )
    db.add(fu)
    db.commit()
    db.refresh(fu)
    return fu


@router.delete("/{followup_id}", status_code=204)
def delete_followup(
    followup_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    fu_obj = (
        db.query(FollowUp)
        .filter(FollowUp.id == followup_id, FollowUp.owner_id == user.id)
        .first()
    )
    if not fu_obj:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    db.delete(fu_obj)
    db.commit()
    return None
