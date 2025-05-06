def test_check_eligibility(client, monkeypatch):
    class FakeGRPCResponse:
        def __init__(self):
            self.patient_id = "P123"
            self.status = "ELIGIBLE"

    def fake_check_eligibility(request):
        return FakeGRPCResponse()

    monkeypatch.setattr(
        "care_gateway.api_flask.resources.eligibility.eligibility_stub.CheckEligibility",
        fake_check_eligibility,
    )

    response = client.get("/eligibility/?patient_id=P123")
    assert response.status_code == 200
    data = response.get_json()
    assert data["patient_id"] == "P123"
    assert data["status"] == "ELIGIBLE"
