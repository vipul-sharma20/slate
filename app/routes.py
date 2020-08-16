import os
import json
from datetime import datetime

from flask import request, make_response, jsonify
from flask import current_app as app
from slack import WebClient
from slack.errors import SlackApiError
from slack.signature import SignatureVerifier

from app.constants import (
    STANDUP_CHANNEL_ID,
    ALL,
    ACTIVE,
    INACTIVE,
)
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

    return make_response("invalid request", 403)


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
        todays_datetime = datetime(
            datetime.today().year, datetime.today().month, datetime.today().day
        )

        submissions = Submission.query.filter(
            Submission.created_at >= todays_datetime
        ).all()
        client.chat_postMessage(
            channel=STANDUP_CHANNEL_ID, blocks=build_standup(submissions)
        )

        return make_response("", 200)
    except SlackApiError as e:
        return make_response("Failed", 200)


@app.route("/api/add_standup/", methods=["POST"])
def add_standup():
    payload = request.json
    if payload:
        standup = Standup(**payload)
        db.session.add(standup)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/api/update_standup/", methods=["PUT"])
def update_standup():
    payload = request.json
    if payload:
        Standup.query.get(payload.get("id")).update(**payload)
        db.session.commit()

        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/api/active_standups/", methods=["GET"])
def active_standups():
    status = request.args.get("status", ALL)

    # remove all keys from dict starting with "_"
    filter_keys = lambda x: {k: v for k, v in x.items() if not k.startswith("_")}

    if status == ACTIVE:
        standups = Standup.query.filter_by(is_active=True).all()
    elif status == INACTIVE:
        standups = Standup.query.filter_by(is_active=False).all()
    else:
        standups = Standup.query.all()

    filtered_standups = [filter_keys(standup.__dict__) for standup in standups]

    return jsonify({"success": True, "standups": filtered_standups})


# Delete all previous submissions
@app.route("/api/delete_submissions/", methods=["DELETE"])
def delete_standup():
    todays_datetime = datetime(
        datetime.today().year, datetime.today().month, datetime.today().day
    )
    Submission.query.filter(Submission.created_at < todays_datetime).delete()


@app.route("/health/", methods=["GET"])
def health_check():
    return make_response("Alive!", 200)
