import os
import json
import math
from datetime import datetime

import requests
from slack import WebClient

from app.models import User, Submission
from app.constants import (
    STANDUP_CHANNEL_ID,
    STANDUP_INFO_SECTION,
    STANDUP_SECTION_DIVIDER,
    SUBMIT_TEMPLATE_SECTION_1,
    SUBMIT_TEMPLATE_SECTION_2,
    CAT_API_HOST,
)

client = WebClient(token=os.environ["SLACK_API_TOKEN"])


# Format standups in the Slack's block syntax
def build_standup(submissions, is_single=False) -> list:
    formatted_standup: list = []

    if not is_single:
        formatted_standup.append(STANDUP_INFO_SECTION)

    for submission in submissions:
        standup_user_section = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ""},
        }
        standup_user_section["text"]["text"] = f"<@{submission.user.user_id}>"
        formatted_standup.append(standup_user_section)

        standup_json = json.loads(submission.standup_submission)
        blocks = standup_json.get("blocks", [])
        values = standup_json.get("state", {}).get("values", {})

        standup_content_section = {"type": "section", "fields": []}

        for block in blocks:
            block_id = block.get("block_id", "")
            action_id = block.get("element", {}).get("action_id", "")

            title = block.get("label", {}).get("text", "")
            content = values.get(block_id, {}).get(action_id, {}).get("value", "")

            standup_field = {"type": "mrkdwn", "text": f"\n*{title}*\n{content}\n"}
            standup_content_section["fields"].append(standup_field)

        formatted_standup.append(standup_content_section)
        formatted_standup.append(STANDUP_SECTION_DIVIDER)
    return formatted_standup


# Handle after standup submission process
def after_submission(submission, payload) -> None:
    now = datetime.now().time()
    client = WebClient(token=os.environ["SLACK_API_TOKEN"])

    publish_time = datetime.strptime(
        os.environ.get("STANDUP_PUBLISH_TIME", "13:00"), "%H:%M"
    ).time()

    if now > publish_time:
        client.chat_postMessage(
            channel=STANDUP_CHANNEL_ID, blocks=build_standup([submission], True)
        )

    client.chat_postMessage(
        channel=submission.user.user_id, blocks=after_submission_message()
    )


# Random friendly message
def after_submission_message() -> list:
    blocks = [SUBMIT_TEMPLATE_SECTION_1]

    if os.environ.get("CAT_MODE", 0):
        response = requests.get(
            CAT_API_HOST + "/api/images/get?type=jpg&size=med&format=json", timeout=3
        )

        if response.ok:
            response_json = response.json()
            item_url = response_json[0].get("url")
            blocks.append(SUBMIT_TEMPLATE_SECTION_2)

            blocks.append(
                {
                    "type": "image",
                    "title": {"type": "plain_text", "text": "image", "emoji": True},
                    "image_url": f"{item_url}",
                    "alt_text": "image",
                }
            )
    return blocks


# Send direct text message
def send_direct_message(user_id, text) -> None:
    client.chat_postMessage(channel=user_id, text=text)


# Check if new submission is eligible
def is_submission_eligible(payload: dict) -> bool:
    """
    TODO: Don't allow multiple submissions by same user on same day
    """
    return True


# Post standup user stats after publish
def post_publish_stat() -> list:
    no_submit_users: list = []

    users = User.query.filter_by(is_active=True).all()

    for user in users:
        todays_datetime = datetime(
            datetime.today().year, datetime.today().month, datetime.today().day
        )

        submission = user.submission.filter(
            Submission.created_at >= todays_datetime
        ).first()
        if submission is None:
            no_submit_users.append(f"<@{user.user_id}>")

    return no_submit_users


# Find how much time left to report
def time_left() -> str:
    text: str = ""

    publish_time = datetime.strptime(
        os.environ.get("STANDUP_PUBLISH_TIME", "13:00"), "%H:%M"
    ).time()

    publish_datetime = datetime(
        datetime.today().year,
        datetime.today().month,
        datetime.today().day,
        publish_time.hour,
        publish_time.minute,
    )

    now = datetime.now()
    diff = (publish_datetime - now).seconds

    if diff >= 3600:
        hours = math.floor(diff / 3600)
        text += f"{hours} hours "
        diff -= hours * 3600
    if diff >= 60:
        minutes = math.floor(diff / 60)
        text += f"{minutes} minutes "
        diff -= minutes * 60

    return text


# Show pretty dump of questions from block kit for standup
def format_standup(standup) -> dict:
    pretty_dict: dict = {**standup}
    pretty_dict["questions"] = []

    standup_blocks = json.loads(standup["standup_blocks"])
    blocks = filter(lambda x: x["type"] == "input", standup_blocks["blocks"])

    for block in blocks:
        pretty_dict["questions"].append(block["label"]["text"])

    return pretty_dict


# Convert list of questions to block kit form
def questions_to_blockkit(questions: list) -> dict:
    blockkit_form = {
        "title": {"type": "plain_text", "text": "Daily Standup", "emoji": True},
        "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
        "type": "modal",
        "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
        "blocks": [],
    }

    for question in questions:
        block_template = {
            "type": "input",
            "label": {"type": "plain_text", "text": "", "emoji": True},
            "element": {"type": "plain_text_input", "multiline": True},
        }
        block_template["label"]["text"] = question
        blockkit_form["blocks"].append(block_template)
    return blockkit_form


# prepare data for Standup table
def prepare_standup_table_data(**payload):
    data: dict = {}

    data["is_active"] = payload.get("is_active", False)
    data["standup_blocks"] = json.dumps(payload.get("standup_blocks", {}))
    data["trigger"] = payload.get("trigger", "")

    return data


# Prepare response for fetch user APIs
def prepare_user_response(user):
    return {
        "id": user.id,
        "username": user.username,
        "is_active": user.is_active,
        "standup_id": user.standup_id,
    }


# validate /api/add_standup/ API payload
def is_standup_valid(**payload):
    if all(key in payload for key in ["questions", "is_active", "trigger"]):
        return True
    return False


# validate /api/get_submission/ API params
def is_get_submission_valid(**params):
    if all(key in params for key in ["id"]):
        return True
    return False
