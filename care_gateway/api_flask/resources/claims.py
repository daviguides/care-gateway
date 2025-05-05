from flask import Blueprint, jsonify, abort
from care_gateway.db.database import get_session
from care_gateway.db.sqlalchemy_models.models import Claim
from care_gateway.api_flask.schemas.claim import ClaimSchema

claims_blueprint = Blueprint("claims", __name__)

schema = ClaimSchema()
many_schema = ClaimSchema(many=True)


@claims_blueprint.route("/", methods=["GET"])
def list_claims():
    session = get_session()
    claims = session.query(Claim).all()
    return jsonify(many_schema.dump(claims))


@claims_blueprint.route("/<int:claim_id>", methods=["GET"])
def get_claim(claim_id):
    session = get_session()
    claim = session.get(Claim, claim_id)
    if not claim:
        abort(404, "Claim not found")
    return jsonify(schema.dump(claim))
