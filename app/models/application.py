from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)

    position: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="applied", nullable=False)
    applied_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    company = relationship("Company", back_populates="applications")
    owner = relationship("User")
    followups = relationship("FollowUp", back_populates="application", cascade="all, delete-orphan")
    