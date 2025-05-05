from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Time,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ClaimRecord(Base):
    __tablename__ = "claim_records"

    claim_id = Column(String, primary_key=True)
    success = Column(Boolean, nullable=False)


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reference_id = Column(String, nullable=False)
    patient_name = Column(String, nullable=False)
    patient_dob = Column(Date, nullable=False)
    claim_amount = Column(Float, nullable=False)
    imported_from = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    service_lines = relationship(
        "ServiceLine", back_populates="claim", cascade="all, delete-orphan"
    )
    events = relationship(
        "ClaimEvent", back_populates="claim", cascade="all, delete-orphan"
    )


class ServiceLine(Base):
    __tablename__ = "service_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(Integer, ForeignKey("claims.id"))
    procedure_code = Column(String)
    charge_amount = Column(Float)
    service_date = Column(Date)

    claim = relationship("Claim", back_populates="service_lines")


class ClaimEvent(Base):
    __tablename__ = "claim_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    event_type = Column(String, nullable=False)
    event_date = Column(Date)
    event_datetime = Column(DateTime(timezone=True))
    event_time = Column(DateTime)
    raw_code = Column(String)
    raw_format = Column(String)

    claim = relationship("Claim", back_populates="events")
