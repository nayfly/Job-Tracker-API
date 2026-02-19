from datetime import date, timedelta

import pytest

from app.schemas.application import ApplicationCreate
from app.schemas.followup import FollowUpCreate


def test_application_date_validation():
    today = date.today()
    # valid
    ApplicationCreate(position="x", company_id=1, applied_at=today)

    # future date should raise
    with pytest.raises(ValueError):
        ApplicationCreate(position="x", company_id=1, applied_at=today + timedelta(days=1))


def test_followup_note_validation():
    # empty note
    with pytest.raises(ValueError):
        FollowUpCreate(application_id=1, note="   ")

    # too long
    with pytest.raises(ValueError):
        FollowUpCreate(application_id=1, note="x" * 1001)

    # valid
    FollowUpCreate(application_id=1, note="hello")
