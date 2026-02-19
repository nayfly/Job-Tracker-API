from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

Status = Literal["applied", "interview", "offer", "rejected"]


class ApplicationCreate(BaseModel):
    position: str
    company_id: int
    status: Status = "applied"
    applied_at: date | None = None

    @field_validator("applied_at")
    @classmethod
    def validate_date(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("applied_at cannot be in the future")
        return v


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: str
    status: Status
    applied_at: date | None
    company_id: int
    