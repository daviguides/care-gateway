import grpc
from flask import Blueprint, abort, jsonify, request

from care_gateway.api_flask.schemas.claim_event import ClaimEventSchema
from care_gateway.db.sqlalchemy_models.models import ClaimEvent
from care_gateway.db.sqlalchemy_models.session import get_session
from care_gateway.service_grpc.proto.claims import (
    claims_pb2,
    claims_pb2_grpc,
)

claim_events_blueprint = Blueprint("claim_events", __name__)
schema = ClaimEventSchema()
many_schema = ClaimEventSchema(many=True)

channel = grpc.insecure_channel("localhost:50052")
claims_stub = claims_pb2_grpc.ClaimsServiceStub(channel)


@claim_events_blueprint.route("/", methods=["GET"])
def list_events():
    session = get_session()
    events = session.query(ClaimEvent).all()
    return jsonify(many_schema.dump(events))


@claim_events_blueprint.route("/<string:event_id>", methods=["GET"])
def get_event(event_id):
    session = get_session()
    event = session.get(ClaimEvent, event_id)
    if not event:
        abort(404, "Event not found")
    return jsonify(schema.dump(event))


@claim_events_blueprint.route("/by-claim/<int:claim_id>", methods=["GET"])
def list_events_by_claim(claim_id):
    session = get_session()
    events = session.query(ClaimEvent).filter(ClaimEvent.claim_id == claim_id).all()
    return jsonify(many_schema.dump(events))


@claim_events_blueprint.route("/", methods=["POST"])
def create_event():
    data = request.json
    session = get_session()

    event = ClaimEvent(
        claim_id=data["claim_id"],
        event_type=data["event_type"],
        details=data.get("details"),
    )
    session.add(event)
    session.commit()
    return jsonify(event.__dict__), 201


@claim_events_blueprint.route("/submit", methods=["POST"])
def submit_claim_event():
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
