import json
from datetime import datetime, time

from slack_sdk.errors import SlackApiError
from flask import make_response

import app.utils as utils
import app.constants as constants
from app.models import Team, Standup, User, Submission, db
from app import client


# Handler for new/existing standup configuration
def configure_standup_handler(**kwargs):
    payload = kwargs.get("data", {})
    _, team_name = payload.get("view", {}).get("callback_id", "").split("%")
    blocks = payload["view"]["blocks"]
    submit_list = []

    for block in blocks:
        print(block)
        block_id = block.get("block_id", "")
        action_id = block.get("element", {}).get("action_id", "")

        if block_id in ["channels_select", "timepicker_select"]:
            action_id = block.get("accessory", {}).get("action_id", "")
        print(action_id)

        values = payload["view"].get("state", {}).get("values", {})
        if action_id == "multi_users_select-action":
            submit_list.append(values.get(block_id, {}).get(
                action_id, {}).get("selected_users", []))
        elif action_id == "channels_select":
            submit_list.append(values.get(block_id, {}).get(
                action_id, {}).get("selected_channel", []))
        elif action_id == "timepicker_action":
            submit_list.append(values.get(block_id, {}).get(
                action_id, {}).get("selected_time", []))
        else:
            submit_list.append(values.get(block_id, {}).get(
                action_id, {}).get("value", ""))

    values = list(filter(lambda x: x != "", submit_list))
    user_list, questions, publish_channel, publish_time = values
    publish_time = datetime.strptime("13:00", "%H:%M").time()

    # Get team
    team = Team.query.filter_by(name=team_name).first()
    if not team:
        team = Team(name=team_name)

        db.session.add(team)
        db.session.commit()

    # Get all active users for this team
    users = (
        db.session.query(User)
        .join(Team.user)
        .filter(Team.id == team.id, User.is_active)
    )
    user_ids = [user.user_id for user in users]

    # Users to remove
    remove_user_list = set(user_ids) - set(user_list)
    for user_id in remove_user_list:
        user = User.query.filter_by(user_id=user_id).first()
        teams = []
        for team in user.team:
            if team.name != team_name:
                teams.append(team)
        user.team = teams

        db.session.add(user)
        db.session.commit()

    # Users to add
    add_user_list = set(user_list) - set(user_ids)
    for user_id in add_user_list:
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            user = User(user_id=user_id, is_active=True, team=[team])
        else:
            if team not in user.team:
                user.team.append(team)

        db.session.add(user)
        db.session.commit()

    # Create or update standup
    questions = questions.split("\n")
    blockkit_form = utils.questions_to_blockkit(questions)
    blockkit_form["callback_id"] = f"submit_standup%{team_name}"

    standup = Standup.query.filter(Standup.trigger == team_name).first()
    if not standup:
        standup = Standup(standup_blocks=json.dumps(blockkit_form),
                          trigger=team_name,
                          team=team,
                          publish_time=publish_time,
                          publish_channel=publish_channel)
        team.standup = standup
        db.session.add(standup)
        db.session.commit()
        db.session.add(standup)
        db.session.commit()
    else:
        standup.standup_blocks = json.dumps(blockkit_form)
        standup.publish_time = publish_time
        standup.publish_channel = publish_channel
        db.session.add(standup)
        db.session.commit()


# Handler for new standup submission
def submit_standup_handler(**kwargs):
    payload = kwargs.get("data")
    standup_submission = json.dumps(payload.get("view"))

    if payload and utils.is_submission_eligible(payload):
        user_payload = payload.get("user", {})
        _, team_name = payload.get("view", {}).get("callback_id", "").split("%")

        user = User.query.filter_by(user_id=user_payload.get("id")).first()
        standup = Standup.query.filter(Standup.trigger == team_name).first()

        todays_datetime = datetime(
            datetime.today().year, datetime.today().month, datetime.today().day
        )

        is_edit = False
        if submission := utils.submission_exists(user, standup):
            client.chat_postMessage(channel=user.user_id,
                                    text=constants.SUBMISSION_UPDATED_MESSAGE)
            submission.standup_submission = standup_submission
            is_edit = True
        else:
            submission = Submission(user_id=user.id,
                                    standup_submission=standup_submission,
                                    standup_id=standup.id,
                                    standup=standup)

        db.session.add(submission)
        db.session.commit()

    utils.after_submission(submission, is_edit)


# Open view to configure standup
def open_configure_view(**kwargs):
    data = kwargs.get("data")
    config_blocks: List = dict(constants.CONFIGURE_VIEW)

    try:
        command, team_name = data.get("text").split(" ")
    except ValueError:
        return make_response(
                    f"Slash command format is `/standup configure <team-name>`.",
                    200,
                )

    team = Team.query.filter_by(name=team_name).first()

    if team:
        # Prepare standup question list to put in textfield
        standup_json = json.loads(team.standup.standup_blocks)

        blocks = standup_json.get("blocks", [])
        questions = filter(lambda block: block["type"] == "input", blocks)
        questions = map(lambda block: block["label"]["text"], questions)

        # Get all active users for this team
        users = (
            db.session.query(User)
            .join(Team.user)
            .filter(Team.id == team.id, User.is_active)
        ).all()

        users_list = [user.user_id for user in users]

        # Add initial values
        users_input_block = config_blocks["blocks"][1]
        standup_input_block = config_blocks["blocks"][2]
        channel_block = config_blocks["blocks"][5]
        publish_time_block = config_blocks["blocks"][7]

        users_input_block["element"]["initial_users"] = users_list
        standup_input_block["element"]["initial_value"] = "\n".join(questions)
        channel_block["accessory"]["initial_channel"] = team.standup.publish_channel
        publish_time_block["accessory"]["initial_time"] = time.strftime(team.standup.publish_time, "%H:%M")

    config_blocks["callback_id"] = f"configure_standup%{team_name}"

    client.views_open(trigger_id=data.get("trigger_id"),
                      view=config_blocks)


# Open standup view for a user
def open_standup_view(**kwargs):
    user_id = kwargs.get("user_id")
    data = kwargs.get("data", None)
    trigger_type = kwargs.get("trigger_type", constants.BUTTON_TRIGGER)

    try:
        user = User.query.filter_by(user_id=user_id).first()
        if trigger_type == constants.BUTTON_TRIGGER:
            team = (
                db.session.query(Team)
                .join(User.team)
                .filter(User.id == user.id)
                .first()
            )
        else:
            team_name = data.get("text")
            print(team_name)
            if not team_name:
                message = f"Slash command format is `/standup <team-name>`.\nYour commands: {', '.join(utils.get_user_slash_commands(user))}"
                client.chat_postMessage(channel=user.user_id, text=message)
            team = Team.query.filter_by(name=team_name).first()

        # TODO: Check if this user it allowed in this team's standup especially
        # in the case of slash command trigger.
        standup = team.standup

        if submission := utils.submission_exists(user, standup):
            client.views_open(
                trigger_id=data.get("trigger_id"),
                view=open_edit_view(standup, submission)
            )

        client.views_open(
            trigger_id=data.get("trigger_id"),
            view=utils.get_standup_view(standup)
        )
        return make_response("", 200)
    except SlackApiError as e:
        code = e.response["error"]
        return make_response(f"Failed to open a modal due to {code}", 200)
    except AttributeError:
        return make_response(
            f"No user details or standup exists for this request.\n{constants.NO_USER_ERROR_MESSAGE}",
            200,
        )


# Create block kit filled with existing responses for standup
def open_edit_view(standup: Standup, submission: Submission) -> str:
    standup_json = json.loads(submission.standup_submission)
    submission_text_list: List = []

    # Create list of existing responses
    blocks = standup_json.get("blocks", [])
    for block in blocks:
        block_id = block.get("block_id", "")
        action_id = block.get("element", {}).get("action_id", "")

        values = standup_json.get("state", {}).get("values", {})
        submission_text_list.append(values.get(
            block_id, {}).get(action_id, {}).get("value", ""))

    # Create edit view filled with responses
    standup_blocks = json.loads(standup.standup_blocks)
    filled_blocks: List = []
    for idx, block in enumerate(standup_blocks.get("blocks", [])):
        if block["type"] == "input":
            block["element"]["initial_value"] = submission_text_list[idx]
        filled_blocks.append(block)
    standup_blocks["blocks"] = filled_blocks
    standup_blocks["callback_id"] = f"submit_standup%{standup.trigger}"

    return json.dumps(standup_blocks)
