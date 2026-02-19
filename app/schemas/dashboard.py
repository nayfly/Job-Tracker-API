from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel

from app.schemas.application import Status
from app.schemas.followup import FollowUpOut


class DashboardSummary(BaseModel):
    counts_by_status: Dict[Status, int]
    recent_followups: List[FollowUpOut]
