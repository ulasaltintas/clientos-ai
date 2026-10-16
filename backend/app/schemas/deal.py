
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enums.deal import DealStage


class DealCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)

    value: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    stage: DealStage = DealStage.LEAD

    company_id: int = Field(gt=0)

    contact_id: int | None = Field(default=None, gt=0)

    expected_close_date: date | None = None

    @field_validator("value", mode="before")
    @classmethod
    def validate_value_type(cls, value):
        if isinstance(value, bool) or not isinstance(
            value, (str, int, Decimal)
        ):
            raise ValueError(
                "Value must be a decimal string or integer"
            )
        return value


class DealResponse(DealCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DealUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    value: Decimal = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    stage: DealStage = None

    company_id: int = Field(default=None, gt=0)

    contact_id: int | None = None

    expected_close_date: date | None = None

    @field_validator("value", mode="before")
    @classmethod
    def validate_value_type(cls, value):
        if value is None:
            return value
        if isinstance(value, bool) or not isinstance(
            value, (str, int, Decimal)
        ):
            raise ValueError(
                "Value must be a decimal string or integer"
            )
        return value
