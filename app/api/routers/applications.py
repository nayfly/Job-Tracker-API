from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.application import Application
from app.models.followup import FollowUp
from sqlalchemy import func
from app.models.company import Company
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationOut, Status

router = APIRouter()

from app.schemas.dashboard import DashboardSummary


@router.get("/", response_model=list[ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    status: Status | None = None,
    company_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("applied_at", pattern="^(applied_at|status|id)$"),
    desc: bool = False,
):
    query = db.query(Application).filter(Application.owner_id == user.id)
    if status:
        query = query.filter(Application.status == status)
    if company_id:
        query = query.filter(Application.company_id == company_id)

    col = getattr(Application, order_by)
    if desc:
        col = col.desc()
    query = query.order_by(col)

    return query.offset(offset).limit(limit).all()


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DashboardSummary:
    # count applications by status
    rows = (
        db.query(Application.status, func.count(Application.id))
        .filter(Application.owner_id == user.id)
        .group_by(Application.status)
        .all()
    )
    counts = {status: count for status, count in rows}

    recent = (
        db.query(FollowUp)
        .join(Application, FollowUp.application_id == Application.id)
        .filter(Application.owner_id == user.id)
        .order_by(FollowUp.created_at.desc())
        .limit(5)
        .all()
    )
    return DashboardSummary(counts_by_status=counts, recent_followups=recent)


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


# --- partial update support -------------------------------------------------
from datetime import date
from pydantic import field_validator, BaseModel


class ApplicationPatch(BaseModel):
    position: str | None = None
    status: Status | None = None
    applied_at: date | None = None
    company_id: int | None = None

    @field_validator("applied_at")
    @classmethod
    def validate_date(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("applied_at cannot be in the future")
        return v


@router.patch("/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: int,
    payload: ApplicationPatch,
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

    for attr, val in payload.model_dump(exclude_unset=True).items():
        setattr(app_obj, attr, val)
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj


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
