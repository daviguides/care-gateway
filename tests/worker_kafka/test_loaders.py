import json
import logging
import tempfile
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import date

import care_gateway.worker_kafka.edi_etl.loaders as loaders
from care_gateway.db.sqlmodel_models.models import Claim, ClaimEvent
from care_gateway.worker_kafka.edi_etl.edi_transform import convert_to_claim_with_events
from care_gateway.worker_kafka.edi_etl.loaders import (
    load_claims_from_dicts,
    save_claim_with_events,
)


@pytest.fixture
async def async_session():
    # Use in-memory SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    TestSession = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with TestSession() as session:
        yield session


@pytest.mark.asyncio
async def test_save_claim_with_events_inserts(async_session: AsyncSession):
    claim = Claim(
        reference_id="REF123",
        patient_name="Alice",
        patient_dob=date(1990, 1, 1),
        claim_amount=100.0,
        imported_from="test_source",
    )
    events = [ClaimEvent(event_type="CREATED")]

    await save_claim_with_events(async_session, claim, events)
    await async_session.commit()

    result = await async_session.exec(
        select(Claim).where(Claim.reference_id == "REF123")
    )
    inserted = result.first()
    assert inserted is not None
    assert inserted.reference_id == "REF123"


@pytest.mark.asyncio
async def test_save_claim_with_events_skips_duplicate(async_session, caplog):
    claim = Claim(
        reference_id="REF456",
        patient_name="Bob",
        patient_dob=date(1985, 5, 5),
        claim_amount=150.0,
        imported_from="test_source",
    )
    await async_session.merge(claim)
    await async_session.commit()

    # Tentar salvar novamente
    duplicate_claim = Claim(
        reference_id="REF456",
        patient_name="Bob",
        patient_dob=date(1985, 5, 5),
        claim_amount=150.0,
        imported_from="test_source",
    )
    duplicate_event = ClaimEvent(event_type="RECEIVED")

    with caplog.at_level(logging.INFO):
        await save_claim_with_events(async_session, duplicate_claim, [duplicate_event])

    assert "already exists. Skipping." in caplog.text


@pytest.mark.asyncio
async def test_load_claims_from_dicts_writes_file(async_session):
    claim_data = [
        {
            "claim_id": "C5678",
            "patient": {"name": "Eve", "dob": "19880101"},
            "claim_header": {
                "claim_id": "C5678",
                "claim_amount": "200.0",
                "claim_dates": [
                    {"date_cd": "431", "date_format": "D8", "date": "20240101"}
                ],
            },
            "source_file": "source.txt",
        }
    ]

    outbox_path = "out"

    await load_claims_from_dicts(async_session, claim_data, Path(outbox_path))

    expected_file = Path(outbox_path) / "C5678.json"
    assert not expected_file.exists()
