import os
import json
import math
from datetime import datetime
from functools import wraps
from typing import List, Dict, Any, Iterator, Tuple

import requests
from flask import request, jsonify
from sqlalchemy import and_

from app import app_cache, client
from app.models import Submission, PostSubmitActionEnum, User, Standup, \
    StandupThread, Team, db
from app.constants import (
    STANDUP_INFO_SECTION,
    STANDUP_SECTION_DIVIDER,
    STANDUP_HELP_SECTION,
    SUBMIT_TEMPLATE_SECTION_1,
    SUBMIT_TEMPLATE_SECTION_2,
    SUBMIT_TEMPLATE_SECTION_3,
    EDIT_DIALOG_SECTION,
    APP_CONTEXT_SECTION,
    CAT_API_HOST,
    NOTIFICATION_BLOCKS,
)


def authenticate(func):
    @wraps(func)
    def check_authorization(*args, **kwargs):
        if os.environ.get("ENVIRONMENT", "DEBUG") == "DEBUG":
            return func(*args, **kwargs)
        else:
            auth_key = request.headers.get("Authorization", "")
            if app_cache.get(auth_key):
                return func(*args, **kwargs)
            else:
                return (
                    jsonify(
                        {
                            "sucess": False,
                            "reason": 'Invalid token. Send token as "Authorization" header',
                        }
                    ),
                    401,
                )

    return check_authorization


# Format standups in the Slack's block syntax
def build_standup(submissions: List[Submission], is_single: bool = False) -> List[Dict[str, Any]]:
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

        for block in blocks:
            if block.get("type") == "section":
                continue

            standup_content_section = {"type": "section", "text": {}}

            block_id = block.get("block_id", "")
            action_id = block.get("element", {}).get("action_id", "")

            title = block.get("label", {}).get("text", "")
            content = values.get(block_id, {}).get(action_id, {}).get("value", "")
            content = beautify_slack_markup(content)

            standup_field = {"type": "mrkdwn", "text": f"\n*{title}*\n{content}\n"}
            standup_content_section["text"] = standup_field

            formatted_standup.append(standup_content_section)
        formatted_standup.append(STANDUP_SECTION_DIVIDER)
    return formatted_standup


# Beautify text content
def beautify_slack_markup(markup: str) -> str:
    markup = markup.replace("* ", "• ")
    markup = markup.replace("- ", "• ")

    return markup


# Slack can't post more than 50 blocks. This function will chunk the
# blocks into blocks of 50 or chunk_size
def chunk_blocks(blocks: List[Dict], chunk_size: int) -> Iterator[List[Dict[str, Any]]]:
    for i in range(0, len(blocks), chunk_size):
        yield blocks[i:i + chunk_size]


# Handle after standup submission process
def after_submission(submission: Submission, is_edit: bool = False) -> None:
    now = datetime.now().time()
    publish_time = submission.standup.publish_time

    blocks = build_standup([submission], True)
    if now > publish_time:
        todays_datetime = datetime(
            datetime.today().year, datetime.today().month, datetime.today().day
        )
        thread = StandupThread.query.filter(
            and_(
                StandupThread.standup == submission.standup,
                StandupThread.created_at >= todays_datetime,
            )).first()

        channel = submission.standup.publish_channel
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread.thread_id,
            blocks=blocks,
        )
        update_users_left_info(channel, thread.thread_id,
                               submission.standup.team.id)

    if not is_edit:
        client.chat_postMessage(
            channel=submission.user.user_id,
            blocks=[SUBMIT_TEMPLATE_SECTION_1] +
            add_optional_block(submission.user.post_submit_action)
        )

    # TODO: Add edit options for people in multiple teams. This ensures no
    # edits right now because button click events are not designed to handle
    # different scenarios
    if len(submission.user.team) > 1:
        blocks = [SUBMIT_TEMPLATE_SECTION_3] + blocks + [APP_CONTEXT_SECTION]
    else:
        edit_dialog = dict(EDIT_DIALOG_SECTION)
        edit_dialog["block_id"] = f"open_dialog%{submission.standup.trigger}"
        blocks = [SUBMIT_TEMPLATE_SECTION_3] + blocks + \
            [EDIT_DIALOG_SECTION] + [APP_CONTEXT_SECTION]

    client.chat_postMessage(
        channel=submission.user.user_id,
        blocks=blocks,
    )


# Random friendly message
def add_optional_block(post_submit_action: PostSubmitActionEnum) -> List[Dict[str, Any]]:
    blocks: List = []

    if post_submit_action == PostSubmitActionEnum.cat:
        response = requests.get(
            CAT_API_HOST + "/api/images/get?type=jpg&size=med&format=json", timeout=2
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
    elif post_submit_action == PostSubmitActionEnum.dog:
        pass

    return blocks


# Check if new submission is eligible
def is_submission_eligible(payload: Dict) -> bool:
    """
    TODO: Don't allow multiple submissions by same user on same day
    """
    return True


# Post standup user stats after publish
def post_publish_stat(users: List[User]) -> List[str]:
    no_submit_users: list = []
    users = users.all()

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
def time_left(publish_time: str) -> str:
    text: str = ""

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
def format_standup(standup: Standup) -> Dict[str, Any]:
    pretty_dict: dict = {**standup}
    pretty_dict["questions"] = []

    standup_blocks = json.loads(standup["standup_blocks"])
    blocks = filter(lambda x: x["type"] == "input", standup_blocks["blocks"])

    for block in blocks:
        pretty_dict["questions"].append(block["label"]["text"])

    return pretty_dict


# Convert list of questions to block kit form
def questions_to_blockkit(questions: List[str]) -> Dict[str, Any]:
    blockkit_form = {
        "title": {"type": "plain_text", "text": "Daily Standup", "emoji": True},
        "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
        "type": "modal",
        "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
        "blocks": [],
    }
    blockkit_form["blocks"].append(STANDUP_HELP_SECTION)

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
def prepare_standup_table_data(**payload: Dict[str, Any]) -> Dict[str, Any]:
    data: dict = {}

    data["is_active"] = payload.get("is_active", False)
    data["standup_blocks"] = json.dumps(payload.get("standup_blocks", {}))
    data["trigger"] = payload.get("trigger", "")

    return data


# Prepare response for fetch user APIs
def prepare_user_response(users: List[User]) -> List[Dict]:
    response: List = []

    for user in users:
        response.append({
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active,
            "user_id": user.user_id,
            "team": [team.name for team in user.team],
        })
    return response


# Prepare response for get user submission API
def prepare_user_submission(submission: Submission) -> Dict[str, Any]:
    submission_response = dict(
        created_at=submission.created_at,
        submission_id=submission.id,
        user_id=submission.user_id,
        username=submission.user.username,
        submission=[])

    response_json = json.loads(submission.standup_submission)
    blocks = response_json.get("blocks", [])
    blocks = filter(lambda x: x["type"] == "input", blocks)

    state_dict = response_json.get("state", {})

    for block in blocks:
        block_id = block["block_id"]
        action_id = block["element"]["action_id"]

        question = block["label"]["text"]
        answer = state_dict["values"][block_id][action_id]["value"]

        submission_response["submission"].append(
            {"question": question, "answer": answer}
        )

    return submission_response


# List of slash commands available to a user
def get_user_slash_commands(user: User) -> List[str]:
    return [f"`/standup {team.name}`" for team in user.team]


# Notification message builder
def prepare_notification_message(user: User) -> Tuple[str, List[Any]]:
    num_teams = len(user.team)

    # TODO: Fix team specific notification
    text = f"The standup will be reported in {time_left(user.team[0].standup.publish_time)}."

    if num_teams >= 2:
        triggers = get_user_slash_commands(user)
        text += "\nPlease submit your standups using: " + " ".join(triggers)
        return text, []
    else:
        blocks = NOTIFICATION_BLOCKS[:]
        team_name = user.team[0].name
        blocks[1]["block_id"] = f"open_standup%{team_name}"

        text += f"\nYou can click on the button below or use command: `/standup {team_name}`"

        eta_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text,
            },
        }

        blocks.insert(1, eta_section)
        return text, blocks


# validate /api/add_standup/ API payload
def is_standup_valid(**payload: Dict[str, Any]) -> bool:
    required_keys = ["questions", "is_active", "trigger", "publish_channel"]
    if all(key in payload for key in required_keys):
        return True
    return False


# validate /api/get_submission/ API params
def is_get_submission_valid(**params: Dict[str, Any]) -> bool:
    if all(key in params for key in ["id"]):
        return True
    return False


# Check if submission exists for a user for current day
def submission_exists(user: User, standup: Standup) -> Submission:
    print(standup.trigger)
    todays_datetime = datetime(
        datetime.today().year, datetime.today().month, datetime.today().day
    )

    return Submission.query.filter(
        and_(Submission.user_id == user.id,
             Submission.created_at >= todays_datetime,
             Submission.standup == standup,
             )).first()


# Create block kit view for standup
def get_standup_view(standup: Standup) -> str:
    standup_str = standup.standup_blocks

    standup_blocks = json.loads(standup_str)
    standup_blocks["callback_id"] = f"submit_standup%{standup.trigger}"

    return json.dumps(standup_blocks)


# Get section to show users left for submission
def users_left_section(users: List[str]) -> List[Dict[str, Any]]:
    return [{
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Didn't hear from: {', '.join(users)}"
            }
        ]
    }]


# Update users left message
def update_users_left_info(channel: str, thread_id: str, team_id: int) -> None:
    # Get all active users for this team
    users = (
        db.session.query(User)
        .join(Team.user)
        .filter(Team.id == team_id, User.is_active)
    )

    no_submission_users = post_publish_stat(users)
    client.chat_update(channel=channel,
                       ts=thread_id,
                       blocks=[STANDUP_INFO_SECTION] + users_left_section(no_submission_users))
