import os
import json
import math
from datetime import datetime

import requests
from slack import WebClient

from app.constants import (
    STANDUP_CHANNEL_ID,
    STANDUP_INFO_SECTION,
    STANDUP_USER_SECTION,
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
        standup_user_section = {"type": "section", "text": {"type": "mrkdwn", "text": ""}}
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
