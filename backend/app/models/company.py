from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column #Mapped: python type of model attr, mapped_column:
#defines a column in the table

from app.base import Base

class Company(Base): #SQLAlchemy database model
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    industry: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
