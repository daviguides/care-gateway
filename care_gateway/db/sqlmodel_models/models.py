from datetime import date, datetime, time, timezone

from sqlmodel import Field, Relationship, SQLModel


class ClaimRecord(SQLModel, table=True):
    __tablename__ = "claim_records"

    claim_id: str = Field(primary_key=True)
    success: bool


class Claim(SQLModel, table=True):
    __tablename__ = "claims"

    id: int = Field(default=None, primary_key=True)
    reference_id: str = None
    patient_name: str = None
    patient_dob: date = None
    claim_amount: float = None
    imported_from: str = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    service_lines: list["ServiceLine"] = Relationship(back_populates="claim")
    events: list["ClaimEvent"] = Relationship(back_populates="claim")


class ClaimEvent(SQLModel, table=True):
    __tablename__ = "claim_events"

    id: int | None = Field(default=None, primary_key=True)
    claim_id: int = Field(foreign_key="claims.id")
    event_type: str  # e.g. "Service Start", "Service End", "Discharge Time"
    event_date: date | None = None
    event_datetime: datetime | None = None
    event_time: datetime | None = None
    raw_code: str | None = None  # original EDI code, ex: "434"
    raw_format: str | None = None  # ex: "D8", "TM", "DT", etc.

    claim: Claim = Relationship(back_populates="events")


class ServiceLine(SQLModel, table=True):
    __tablename__ = "service_lines"

    id: int | None = Field(default=None, primary_key=True)
    claim_id: int | None = Field(default=None, foreign_key="claims.id")
    procedure_code: str | None = None
    charge_amount: float | None = None
    service_date: date | None = None

    claim: Claim | None = Relationship(back_populates="service_lines")
