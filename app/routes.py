import os
import json
from datetime import datetime

from flask import request, make_response, jsonify, redirect, url_for
from flask import current_app as app
from slack import WebClient
from slack.errors import SlackApiError

from app.constants import (
    STANDUP_CHANNEL_ID,
    ALL,
    ACTIVE,
    INACTIVE,
    NOTIFICATION_BLOCKS,
    NO_USER_ERROR_MESSAGE,
    POST_PUBLISH_STATS,
    NO_USER_SUBMIT_MESSAGE,
)
from app.models import Submission, Standup, User, db
from app.utils import authenticate
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
            channel=STANDUP_CHANNEL_ID,
            text="Standup complete",
            blocks=utils.build_standup(submissions),
        )
        if POST_PUBLISH_STATS:
            no_submit_users = utils.post_publish_stat()
            message = f"{NO_USER_SUBMIT_MESSAGE} {', '.join(no_submit_users)}"

            client.chat_postMessage(channel=STANDUP_CHANNEL_ID, text=message)

        return make_response(json.dumps(utils.build_standup(submissions)), 200)
    except SlackApiError as e:
        code = e.response["error"]
        return make_response(f"Failed due to {code}", 200)


# APIs start here

# Add user to DB
@app.route("/api/add_user/", methods=["POST"])
@authenticate
def add_user():
    payload = request.json
    if payload:
        user = User(**payload)
        db.session.add(user)
        db.session.commit()
        return jsonify({"sucess": True, "id": user.id})
    return jsonify({"sucess": False})


# Update user
@app.route("/api/update_user/<user_id>/", methods=["PUT"])
@authenticate
def update_user(user_id):
    payload = request.json
    if payload:
        User.query.get(user_id).update(**payload)
        db.session.commit()

        return jsonify({"sucess": True})
    return jsonify({"sucess": False})


# Get user by username
@app.route("/api/get_user/<username>/", methods=["GET"])
@authenticate
def get_user(username):
    try:
        user = User.query.filter_by(username=username).first()
        return jsonify({"success": True, "user": utils.prepare_user_response(user)})
    except:
        return jsonify({"success": False, "reason": "Username does not exist"})


# Get all users
@app.route("/api/get_users/", methods=["GET"])
@authenticate
def get_users():
    users = User.query.all()
    users_response = [utils.prepare_user_response(user) for user in users]
    return jsonify({"success": True, "users": users_response})


# Add a new standup to DB
@app.route("/api/add_standup/", methods=["POST"])
@authenticate
def add_standup():
    payload = request.json
    if utils.is_standup_valid(**payload):
        payload["standup_blocks"] = utils.questions_to_blockkit(
            payload.get("questions")
        )
        data = utils.prepare_standup_table_data(**payload)

        try:
            standup = Standup(**data)
            db.session.add(standup)
            db.session.commit()

            return jsonify({"success": True, "standup_id": standup.id})
        except:
            return jsonify(
                {
                    "success": False,
                    "reason": "Could not save the submitted standup to DB",
                }
            )
    return jsonify(
        {
            "success": False,
            "reason": "Incorrect payload. Required: questions, is_active, trigger",
        }
    )


# Update an existing standup
@app.route("/api/update_standup/<standup_id>/", methods=["PUT"])
@authenticate
def update_standup(standup_id):
    payload = request.json
    if utils.is_standup_valid(**payload):
        try:
            payload["standup_blocks"] = utils.questions_to_blockkit(
                payload.get("questions")
            )
            data = utils.prepare_standup_table_data(**payload)

            Standup.query.get(standup_id).update(**data)
            db.session.commit()
            return jsonify({"success": True})
        except:
            return jsonify(
                {
                    "success": False,
                    "reason": "Could not save the updated standup to DB",
                }
            )
    return jsonify(
        {
            "success": False,
            "reason": "Incorrect payload. Required: questions, is_active, trigger",
        }
    )


@app.route("/api/get_standup/<standup_id>/", methods=["GET"])
@authenticate
def get_standup(standup_id):
    # remove all keys from dict starting with "_"
    filter_keys = lambda x: {k: v for k, v in x.items() if not k.startswith("_")}

    # If id in request args then return standup for id
    if standup_id.isnumeric():
        try:
            standup = Standup.query.filter_by(id=standup_id).first()
            return jsonify(
                {
                    "success": True,
                    "standup": utils.format_standup(filter_keys(standup.__dict__)),
                }
            )
        except:
            return jsonify(
                {
                    "success": False,
                    "reason": f"Standup for id {standup_id} does not exist",
                }
            )
    return jsonify({"success": False, "reason": "Incorrect standup_id."})


# Fetch standups based on their status (active, inactive, all)
@app.route("/api/get_standups/", methods=["GET"])
@authenticate
def get_standups():
    status = request.args.get("status", ALL)

    # remove all keys from dict starting with "_"
    filter_keys = lambda x: {k: v for k, v in x.items() if not k.startswith("_")}

    if status == ACTIVE:
        standups = Standup.query.filter_by(is_active=True).all()
    elif status == INACTIVE:
        standups = Standup.query.filter_by(is_active=False).all()
    else:
        standups = Standup.query.all()

    filtered_standups = [
        utils.format_standup(filter_keys(standup.__dict__)) for standup in standups
    ]

    return jsonify(
        {"success": True, "standups": filtered_standups}
    )


# Delete a standup
@app.route("/api/delete_standup/<standup_id>/", methods=["DELETE"])
@authenticate
def delete_standup(standup_id):
    Standup.query.filter_by(id=standup_id).delete()
    db.session.commit()
    return jsonify({"success": True})


# Delete all previous submissions
@app.route("/api/delete_submissions/", methods=["DELETE"])
@authenticate
def delete_submissions():
    todays_datetime = datetime(
        datetime.today().year, datetime.today().month, datetime.today().day
    )
    Submission.query.filter(Submission.created_at < todays_datetime).delete()


# Notify users who have not submitted the standup yet
@app.route("/api/notify_users/", methods=["GET"])
@authenticate
def notify_users():
    users = User.query.filter_by(is_active=True).all()
    blocks = NOTIFICATION_BLOCKS[:]
    text = f"The standup will be reported in {utils.time_left()}"

    eta_section = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": text,},
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


# Get submission for user id
@app.route("/api/get_submission/<user_id>/", methods=["GET"])
@authenticate
def get_submission(user_id):
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify(
            {
                "success": False,
                "reason": "Invalid date format. Use format yyyy-mm-dd",
            }
        )

    if start_date and end_date:
        submissions = (
            Submission.query.filter_by(user_id=user_id)
            .filter(
                Submission.created_at >= start_date,
                Submission.created_at <= end_date,
            )
            .order_by(Submission.created_at.desc())
            .all()
        )
    elif start_date:
        submissions = (
            Submission.query.filter_by(user_id=user_id)
            .filter(Submission.created_at >= start_date)
            .order_by(Submission.created_at.desc())
            .all()
        )
    elif end_date:
        submissions = (
            Submission.query.filter_by(user_id=user_id)
            .filter(Submission.created_at <= end_date)
            .order_by(Submission.created_at.desc())
            .all()
        )
    else:
        submissions = (
            Submission.query.filter_by(user_id=user_id)
            .order_by(Submission.created_at.desc())
            .limit(50)
            .all()
        )

    return jsonify(
        {
            "success": True,
            "submissions": [
                utils.prepare_user_submission(submission)
                for submission in submissions
            ],
        }
    )


# Get submissions
@app.route("/api/get_submissions/", methods=["GET"])
@authenticate
def get_submissions():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify(
            {"success": False, "reason": "Invalid date format. Use format yyyy-mm-dd",}
        )

    if start_date and end_date:
        submissions = (
            Submission.query.filter(
                Submission.created_at >= start_date, Submission.created_at <= end_date,
            )
            .order_by(Submission.created_at.desc())
            .all()
        )
    elif start_date:
        submissions = (
            Submission.query.filter(Submission.created_at >= start_date)
            .order_by(Submission.created_at.desc())
            .all()
        )
    elif end_date:
        submissions = (
            Submission.query.filter(Submission.created_at <= end_date)
            .order_by(Submission.created_at.desc())
            .all()
        )
    else:
        submissions = (
            Submission.query.order_by(Submission.created_at.desc()).limit(50).all()
        )

    return jsonify(
        {
            "success": True,
            "submissions": [
                utils.prepare_user_submission(submission) for submission in submissions
            ],
        }
    )


# Health check for the server
@app.route("/api/health/", methods=["GET"])
@authenticate
def health_check():
    return make_response("Alive!", 200)

