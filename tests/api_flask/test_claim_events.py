from datetime import datetime, timezone
from care_gateway.db.sqlalchemy_models.models import Claim, ClaimEvent


def test_list_events(client, db_session):
    claim = Claim(
        id=11,
        reference_id="R100",
        patient_name="Ana",
        patient_dob=datetime(1990, 1, 1).date(),
        claim_amount=150.0,
        imported_from="manual",
    )
    db_session.add(claim)

    event = ClaimEvent(
        id=11,
        claim_id=11,
        event_type="CREATED",
    )
    db_session.add(event)
    db_session.commit()

    response = client.get("/claim_events/")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert int(response.json[0]["id"]) == 11


def test_get_event_by_id(client, db_session):
    claim = Claim(
        id=12,
        reference_id="R200",
        patient_name="Bruno",
        patient_dob=datetime(1985, 5, 5).date(),
        claim_amount=200.0,
        imported_from="manual",
    )
    db_session.add(claim)

    event = ClaimEvent(
        id=12,
        claim_id=12,
        event_type="UPDATED",
    )
    db_session.add(event)
    db_session.commit()

    response = client.get("/claim_events/12")
    assert response.status_code == 200
    assert response.json["event_type"] == "UPDATED"
    assert response.json["claim_id"] == 12


def test_get_event_not_found(client):
    response = client.get("/claim_events/9999")
    assert response.status_code == 404


def test_list_events_by_claim(client, db_session):
    claim = Claim(
        id=13,
        reference_id="R300",
        patient_name="Carlos",
        patient_dob=datetime(1980, 3, 3).date(),
        claim_amount=180.0,
        imported_from="api",
    )
    db_session.add(claim)

    db_session.add_all(
        [
            ClaimEvent(
                id=13,
                claim_id=13,
                event_type="CREATED",
            ),
            ClaimEvent(
                id=14,
                claim_id=13,
                event_type="REVIEWED",
            ),
        ]
    )
    db_session.commit()

    response = client.get("/claim_events/by-claim/13")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 2
    event_types = {e["event_type"] for e in response.json}
    assert "CREATED" in event_types
    assert "REVIEWED" in event_types


def test_submit_claim_event(client, monkeypatch):
    class FakeGRPCResponse:
        def __init__(self):
            self.claim_id = "R999"
            self.success = True

    def fake_submit_claim(request):
        return FakeGRPCResponse()

    # substitui o método real do stub
    monkeypatch.setattr(
        "care_gateway.api_flask.resources.claim_events.claims_stub.SubmitClaim",
        fake_submit_claim,
    )

    payload = {"claim_id": "R999"}
    response = client.post("/claim_events/submit", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["claim_id"] == "R999"
    assert data["success"] is True
