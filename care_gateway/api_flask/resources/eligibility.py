from flask import Blueprint, request, jsonify
import grpc

from care_gateway.service_grpc.proto.eligibility import (
    eligibility_pb2,
    eligibility_pb2_grpc,
)

eligibility_blueprint = Blueprint("eligibility", __name__)
channel = grpc.insecure_channel("localhost:50052")
eligibility_stub = eligibility_pb2_grpc.EligibilityServiceStub(channel)


@eligibility_blueprint.route("/", methods=["GET"])
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
