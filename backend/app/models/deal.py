from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base
from app.enums.deal import DealStage

class Deal(Base):
    __tablename__ = "deals"

    __table_args__ = (
        CheckConstraint(
            "value >= 0",
            name="ck_deals_value_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    value: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    stage: Mapped[str] = mapped_column(
        String(20),
        default=DealStage.LEAD.value,
        nullable=False,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )

    contact_id: Mapped[int | None] = mapped_column(
        ForeignKey("contacts.id"),
        nullable=True,
        index=True,
    )

    expected_close_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
