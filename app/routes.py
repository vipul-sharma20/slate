import os
import json
from datetime import datetime

from flask import request, make_response
from flask import current_app as app
from slack import WebClient
from slack.errors import SlackApiError
from slack.signature import SignatureVerifier

from app.constants import STANDUP_MODAL_TEMPLATE, STANDUP_CHANNEL_ID
from app.models import Submission, Standup, db
from app.utils import build_standup


signature_verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])
client = WebClient(token=os.environ["SLACK_API_TOKEN"])


@app.route("/slack/interactive-endpoint/", methods=["POST"])
def interactive_endpoint():
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return make_response("invalid request", 403)

    try:
        standup = Standup.query.filter_by(trigger=request.form.get("text")).first()

        client.views_open(
            trigger_id=request.form.get("trigger_id"), view=standup.standup_blocks
        )
        return make_response("", 200)
    except SlackApiError as e:
        code = e.response["error"]
        return make_response(f"Failed to open a modal due to {code}", 200)

    return make_response("", 404)


def generate_standup_modal() -> dict:
    standup_modal = dict(
        trigger_id=request.form.get("trigger_id"), view=STANDUP_MODAL_TEMPLATE
    )

    return standup_modal


@app.route("/slack/submit_standup/", methods=["POST"])
def standup_modal():
    payload = json.loads(request.form.get("payload"))

    if payload:
        user_payload = payload.get("user", {})
        data = dict(
            user_id=user_payload.get("id"),
            username=user_payload.get("username"),
            standup_submission=json.dumps(payload.get("view")),
        )

        submission = Submission(**data)
        db.session.add(submission)
        db.session.commit()

    return make_response("", 200)


@app.route("/slack/publish_standup/", methods=["GET"])
def publish_standup():

    try:
        todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)

        submissions = Submission.query.filter(Submission.created_at >= todays_datetime).all()
        client.chat_postMessage(
            channel=STANDUP_CHANNEL_ID, blocks=build_standup(submissions)
        )

        return make_response("", 200)
    except SlackApiError as e:
        return make_response("Failed", 200)


@app.route("/slack/delete_standup/", methods=["DELETE"])
def delete_standup():
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    Submission.query.filter(Submission.created_at < todays_datetime).delete()


@app.route("/health/", methods=["GET"])
def health_check():
    return make_response("Alive!", 200)
