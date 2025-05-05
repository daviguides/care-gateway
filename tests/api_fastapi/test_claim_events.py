import pytest
from datetime import datetime, date, timezone
from sqlmodel.ext.asyncio.session import AsyncSession
from care_gateway.db.sqlmodel_models.models import Claim, ClaimEvent


@pytest.mark.asyncio
async def test_list_claim_events(client):
    response = await client.get("/claim_events/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_event_by_id(client, engine_fixture):
    event_id = 2001
    async with AsyncSession(engine_fixture) as session:
        claim = Claim(
            id=1001,
            reference_id="ref-1001",
            patient_name="Maria",
            patient_dob=date(1985, 3, 15),
            claim_amount=150.0,
            imported_from="external_system",
        )
        session.add(claim)
        await session.commit()

        event = ClaimEvent(
            id=event_id,
            claim_id=1001,
            event_type="CREATED",
            created_at=datetime.now(timezone.utc),
        )
        session.add(event)
        await session.commit()

    response = await client.get(f"/claim_events/{event_id}")
    assert response.status_code == 200
    assert response.json()["id"] == event_id


@pytest.mark.asyncio
async def test_event_not_found(client):
    response = await client.get("/claim_events/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_events_by_claim(client, engine_fixture):
    claim_id = 1002
    async with AsyncSession(engine_fixture) as session:
        claim = Claim(
            id=claim_id,
            reference_id="ref-1002",
            patient_name="Lisa",
            patient_dob=date(1990, 6, 1),
            claim_amount=200.0,
            imported_from="external_portal",
        )
        session.add(claim)
        await session.commit()

        session.add_all(
            [
                ClaimEvent(
                    id=2002,
                    claim_id=claim_id,
                    event_type="CREATED",
                    created_at=datetime.now(timezone.utc),
                ),
                ClaimEvent(
                    id=2003,
                    claim_id=claim_id,
                    event_type="UPDATED",
                    created_at=datetime.now(timezone.utc),
                ),
            ]
        )
        await session.commit()

    response = await client.get(f"/claim_events/by-claim/{claim_id}")
    assert response.status_code == 200
    assert len(response.json()) == 2
