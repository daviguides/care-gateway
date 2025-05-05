from flask import Flask
from care_gateway.api_flask.resources.claims import claims_blueprint
from care_gateway.api_flask.resources.claim_events import claim_events_blueprint
from care_gateway.api_flask.resources.eligibility import eligibility_blueprint


def create_app(testing: bool = False, db_session=None) -> Flask:
    app = Flask(__name__)
    app.config["TESTING"] = testing

    if db_session is not None:
        app.config["DB_SESSION"] = db_session

    app.register_blueprint(claims_blueprint, url_prefix="/claims")
    app.register_blueprint(claim_events_blueprint, url_prefix="/claim_events")
    app.register_blueprint(eligibility_blueprint, url_prefix="/eligibility")
    return app
