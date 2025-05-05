from flask import Blueprint, request, jsonify
import grpc

from care_gateway.service_grpc.proto.eligibility import (
    eligibility_pb2,
    eligibility_pb2_grpc,
)

from care_gateway.service_grpc.proto.claims import (
    claims_pb2,
    claims_pb2_grpc,
)

from care_gateway.service_grpc.proto.greeter import (
    greeter_pb2,
    greeter_pb2_grpc,
)

blueprint = Blueprint("routes", __name__)

channel = grpc.insecure_channel("localhost:50052")

# Stubs gRPC
eligibility_stub = eligibility_pb2_grpc.EligibilityServiceStub(channel)
claims_stub = claims_pb2_grpc.ClaimsServiceStub(channel)
greeter_stub = greeter_pb2_grpc.GreeterServiceStub(channel)


@blueprint.route("/eligibility", methods=["GET"])
def check_eligibility():
    patient_id = request.args.get("patient_id", "")
    grpc_response = eligibility_stub.CheckEligibility(
        eligibility_pb2.EligibilityRequest(patient_id=patient_id),
    )
    return jsonify(
        {
            "patient_id": grpc_response.patient_id,
            "status": grpc_response.status,
        }
    )


@blueprint.route("/submit_claim", methods=["POST"])
def submit_claim():
    data = request.get_json(force=True)
    claim_id = data.get("claim_id", "")

    grpc_response = claims_stub.SubmitClaim(
        claims_pb2.ClaimRequest(claim_id=claim_id),
    )

    return jsonify(
        {
            "claim_id": grpc_response.claim_id,
            "success": grpc_response.success,
        }
    )


@blueprint.route("/hello", methods=["GET"])
def say_hello():
    name = request.args.get("name", "World")
    response = greeter_stub.SayHello(
        greeter_pb2.HelloRequest(name=name),
    )
    return jsonify(
        {
            "message": response.message,
        }
    )
