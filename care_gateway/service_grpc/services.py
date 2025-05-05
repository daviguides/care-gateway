from care_gateway.db.sqlalchemy_models.models import ClaimRecord
from care_gateway.db.sqlalchemy_models.session import get_sync_session

from .proto.claims import claims_pb2, claims_pb2_grpc
from .proto.eligibility import eligibility_pb2, eligibility_pb2_grpc
from .proto.greeter import greeter_pb2, greeter_pb2_grpc


class EligibilityService(eligibility_pb2_grpc.EligibilityServiceServicer):
    def CheckEligibility(self, request, context):
        patient_id = request.patient_id.upper()
        if patient_id.startswith("A"):
            status = "ELIGIBLE"
        elif patient_id.startswith("Z"):
            status = "NOT_ELIGIBLE"
        else:
            status = "REVIEW"

        return eligibility_pb2.EligibilityResponse(patient_id=patient_id, status=status)


class ClaimsService(claims_pb2_grpc.ClaimsServiceServicer):
    def SubmitClaim(self, request, context):
        claim_id = request.claim_id.upper()
        success = not claim_id.startswith("X")

        with get_sync_session() as session:
            session.add(ClaimRecord(claim_id=claim_id, success=success))
            session.commit()

        return claims_pb2.ClaimResponse(claim_id=claim_id, success=success)


class GreeterServicer(greeter_pb2_grpc.GreeterServiceServicer):
    def SayHello(self, request, context):
        return greeter_pb2.HelloReply(message=f"Hello, {request.name}!")
