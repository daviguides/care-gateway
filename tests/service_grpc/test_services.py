from care_gateway.service_grpc.services import (
    EligibilityService,
    ClaimsService,
    GreeterServicer,
)
from care_gateway.service_grpc.proto.claims import claims_pb2
from care_gateway.service_grpc.proto.eligibility import eligibility_pb2
from care_gateway.service_grpc.proto.greeter import greeter_pb2


def test_check_eligibility_eligible():
    service = EligibilityService()
    request = eligibility_pb2.EligibilityRequest(patient_id="A123")
    response = service.CheckEligibility(request, context=None)
    assert response.status == "ELIGIBLE"


def test_check_eligibility_not_eligible():
    service = EligibilityService()
    request = eligibility_pb2.EligibilityRequest(patient_id="Z999")
    response = service.CheckEligibility(request, context=None)
    assert response.status == "NOT_ELIGIBLE"


def test_check_eligibility_review():
    service = EligibilityService()
    request = eligibility_pb2.EligibilityRequest(patient_id="M777")
    response = service.CheckEligibility(request, context=None)
    assert response.status == "REVIEW"


def test_submit_claim(monkeypatch):
    service = ClaimsService()

    # mocka o get_sync_session
    class DummySession:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def add(self, record):
            self.record = record

        def commit(self):
            pass

    monkeypatch.setattr(
        "care_gateway.service_grpc.services.get_sync_session", lambda: DummySession()
    )

    request = claims_pb2.ClaimRequest(claim_id="abc123")
    response = service.SubmitClaim(request, context=None)
    assert response.claim_id == "ABC123"
    assert response.success is True


def test_say_hello():
    service = GreeterServicer()
    request = greeter_pb2.HelloRequest(name="Davi")
    response = service.SayHello(request, context=None)
    assert response.message == "Hello, Davi!"
