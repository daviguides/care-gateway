import pytest
from httpx import AsyncClient
from datetime import date
from sqlmodel.ext.asyncio.session import AsyncSession
from care_gateway.db.sqlmodel_models.models import Claim


@pytest.mark.asyncio
async def test_list_claims(client):
    response = await client.get("/claims/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_claim_by_id(client: AsyncClient, engine_fixture):
    async with AsyncSession(engine_fixture) as session:
        claim = Claim(
            id=123,
            reference_id="ref123",
            patient_name="John Doe",
            patient_dob=date(1985, 3, 15),
            claim_amount=150.0,
            imported_from="external_system",
        )
        session.add(claim)
        await session.commit()

    response = await client.get("/claims/123")
    assert response.status_code == 200
    data = response.json()
    assert data["reference_id"] == "ref123"


@pytest.mark.asyncio
async def test_get_claim_not_found(client):
    response = await client.get("/claims/99999")
    assert response.status_code == 404
