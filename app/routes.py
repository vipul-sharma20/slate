import os
import json
from datetime import datetime

from flask import request, make_response, jsonify, redirect, url_for
from flask import current_app as app
from slack import WebClient
from slack.errors import SlackApiError
from slack.signature import SignatureVerifier

from app.constants import (
    STANDUP_CHANNEL_ID,
    ALL,
    ACTIVE,
    INACTIVE,
    NOTIFICATION_BLOCKS,
    NO_USER_ERROR_MESSAGE,
)
from app.models import Submission, Standup, User, db
import app.utils as utils


client = WebClient(token=os.environ["SLACK_API_TOKEN"])


# Callback for entrypoint trigger on Slack (slash command etc.)
@app.route("/slack/standup-trigger/", methods=["POST", "GET"])
def standup_trigger():
    if request.method == "GET":
        data = json.loads(request.args["messages"])
        user_id = data.get("user", {}).get("id")
    else:
        data = request.form
        user_id = data.get("user_id")

    try:
        user = User.query.filter_by(user_id=user_id).first()
        standup = Standup.query.filter_by(id=user.standup_id).first()

        client.views_open(
            trigger_id=data.get("trigger_id"), view=standup.standup_blocks
        )
        return make_response("", 200)
    except SlackApiError as e:
        code = e.response["error"]
        return make_response(f"Failed to open a modal due to {code}", 200)
    except AttributeError:
        utils.send_direct_message(user_id, NO_USER_ERROR_MESSAGE)
        return make_response("No user details or standup exists for this request", 200)

    return make_response("invalid request", 403)


# Callback for form submission on Slack
@app.route("/slack/submit_standup/", methods=["POST"])
def standup_modal():
    payload = json.loads(request.form.get("payload"))

    # Triggered by action button click
    if payload.get("type") == "block_actions":
        return redirect(
            url_for("standup_trigger", messages=request.form.get("payload"))
        )

    if payload and utils.is_submission_eligible(payload):
        user_payload = payload.get("user", {})
        data = dict(standup_submission=json.dumps(payload.get("view")),)

        user = User.query.filter_by(user_id=user_payload.get("id")).first()
        submission = Submission(user_id=user.id, **data)
        db.session.add(submission)
        db.session.commit()

    utils.after_submission(submission, payload)

    return make_response("", 200)


# Request to publish standup to a Slack channel
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
            channel=STANDUP_CHANNEL_ID, text="Standup complete", blocks=utils.build_standup(submissions)
        )

        return make_response(json.dumps(utils.build_standup(submissions)), 200)
    except SlackApiError as e:
        code = e.response["error"]
        return make_response(f"Failed due to {code}", 200)


# APIs start here

# Add user to DB
@app.route("/api/add_user/", methods=["POST"])
def add_user():
    payload = request.json
    if payload:
        user = User(**payload)
        db.session.add(user)
        db.session.commit()
        return jsonify({"sucess": True})
    return jsonify({"sucess": False})


# Add a new standup to DB
@app.route("/api/add_standup/", methods=["POST"])
def add_standup():
    payload = request.json
    if payload:
        standup = Standup(**payload)
        db.session.add(standup)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})


# Update an existing standup
@app.route("/api/update_standup/", methods=["PUT"])
def update_standup():
    payload = request.json
    if payload:
        Standup.query.get(payload.get("id")).update(**payload)
        db.session.commit()

        return jsonify({"success": True})
    return jsonify({"success": False})


# Fetch standups based on their status (active, inactive, all)
@app.route("/api/get_standups/", methods=["GET"])
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


# Delete a standup
@app.route("/api/delete_standup/", methods=["DELETE"])
def delete_standup():
    payload = request.json
    if payload:
        Standup.query.filter_by(id=payload.get("id")).delete()
        db.session.commit()
    return jsonify({"success": True})


# Delete all previous submissions
@app.route("/api/delete_submissions/", methods=["DELETE"])
def delete_submissions():
    todays_datetime = datetime(
        datetime.today().year, datetime.today().month, datetime.today().day
    )
    Submission.query.filter(Submission.created_at < todays_datetime).delete()


# Notify users who have not submitted the standup yet
@app.route("/api/notify_users/", methods=["GET"])
def notify_users():
    users = User.query.filter_by(is_active=True).all()
    blocks = NOTIFICATION_BLOCKS[:]
    text = f"The standup will be reported in {utils.time_left()}"

    eta_section = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text,
        },
    }
    blocks.insert(1, eta_section)

    for user in users:
        todays_datetime = datetime(
            datetime.today().year, datetime.today().month, datetime.today().day
        )

        submission = user.submission.filter(
            Submission.created_at >= todays_datetime
        ).first()
        if submission is None:
            client.chat_postMessage(channel=user.user_id, text=text, blocks=blocks)
    return jsonify({"success": True})


# Health check for the server
@app.route("/api/health/", methods=["GET"])
def health_check():
    return make_response("Alive!", 200)
