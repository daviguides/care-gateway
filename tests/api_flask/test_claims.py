from datetime import date
from care_gateway.db.sqlalchemy_models.models import Claim


def test_list_claims(client, db_session):
    claim = Claim(
        id=1,
        reference_id="REF123",
        patient_name="John Doe",
        patient_dob=date(1990, 1, 1),
        claim_amount=123.45,
        imported_from="test",
    )
    db_session.add(claim)
    db_session.commit()

    response = client.get("/claims/")
    data = response.get_json()
    assert response.status_code == 200
    assert isinstance(data, list)


def test_get_claim_by_id(client, db_session):
    claim = Claim(
        id=2,
        reference_id="REF999",
        patient_name="Jane Smith",
        patient_dob=date(1985, 5, 5),
        claim_amount=200.0,
        imported_from="manual",
    )
    db_session.add(claim)
    db_session.commit()

    response = client.get("/claims/2")
    data = response.get_json()
    assert response.status_code == 200
    assert data["id"] == 2
    assert data["patient_name"] == "Jane Smith"


def test_get_claim_not_found(client):
    response = client.get("/claims/99999")
    assert response.status_code == 404
