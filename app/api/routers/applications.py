from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.application import Application
from app.models.company import Company
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationOut

router = APIRouter()


@router.get("/", response_model=list[ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Application)
        .filter(Application.owner_id == user.id)
        .order_by(Application.id.desc())
        .all()
    )


@router.post("/", response_model=ApplicationOut, status_code=201)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    company = (
        db.query(Company)
        .filter(Company.id == payload.company_id, Company.owner_id == user.id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    app_ = Application(
        company_id=payload.company_id,
        position=payload.position,
        status=payload.status,
        applied_at=payload.applied_at,
        owner_id=user.id,
    )
    db.add(app_)
    db.commit()
    db.refresh(app_)
    return app_


@router.delete("/{application_id}", status_code=204)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app_obj = (
        db.query(Application)
        .filter(Application.id == application_id, Application.owner_id == user.id)
        .first()
    )
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app_obj)
    db.commit()
    return None
