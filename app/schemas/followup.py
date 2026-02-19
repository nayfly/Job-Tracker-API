from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class FollowUpCreate(BaseModel):
    application_id: int
    note: str

    @field_validator("note")
    @classmethod
    def check_length(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("note cannot be empty")
        if len(v) > 1000:
            raise ValueError("note too long (max 1000 characters)")
        return v


class FollowUpOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    note: str
    created_at: datetime
    application_id: int
