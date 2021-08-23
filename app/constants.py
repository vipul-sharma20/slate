import os

ALL = "all"
ACTIVE = "active"
INACTIVE = "inactive"
BUTTON_TRIGGER = "button_trigger"
SLASH_COMMAND_TRIGGER = "slash_command_trigger"

CAT_API_HOST = "https://api.thecatapi.com"

BLOCK_SIZE = 50

NO_USER_ERROR_MESSAGE = (
    "Your user details or standup for your user/team doesn't exist in the database."
)

SUBMISSION_EXISTS_MESSAGE = "You've already made a standup submission for today"
SUBMISSION_UPDATED_MESSAGE = "Your submission has been updated"

POST_PUBLISH_STATS = os.environ.get("POST_PUBLISH_STATS", 0)

NO_USER_SUBMIT_MESSAGE = "Didn't hear from"

STANDUP_INFO_SECTION = {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "*Daily Standup Complete*"},
}

STANDUP_SECTION_DIVIDER = {"type": "divider"}

STANDUP_USER_SECTION = {"type": "section",
                        "text": {"type": "mrkdwn", "text": ""}}

STANDUP_HELP_SECTION = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": "You can use markup to format your messages Documentation <https://slack.com/intl/en-gb/help/articles/202288908-Format-your-messages#use-markup|here>.\n\nProtip:\n `<url|text>`: <https://slack.com/intl/en-gb/help/articles/202288908-Format-your-messages#use-markup|Will render as this>"
    }
}


NOTIFICATION_BLOCKS = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Hello :wave: It's time to start your daily standup",
        },
    },
    {
        "type": "actions",
        "block_id": "open_standup",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "emoji": True, "text": "Open Dialog"},
                "style": "primary",
                "value": "open_dialog",
            }
        ],
    },
]


SUBMIT_TEMPLATE_SECTION_1 = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": "Thanks for submitting today's standup :slightly_smiling_face:",
    },
}


SUBMIT_TEMPLATE_SECTION_2 = {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "Here's a cat for you"},
}

SUBMIT_TEMPLATE_SECTION_3 = {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "*Your responses below*"},
}

EDIT_DIALOG_SECTION = {
    "type": "actions",
    "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "emoji": True, "text": "Edit"},
                "style": "primary",
                "value": "open_dialog",
            }
    ],
}

APP_CONTEXT_SECTION = {
    "type": "context",
    "elements": [
        {
            "type": "mrkdwn",
            "text": "For feature requests, issues etc. please add them in the <https://github.com/vipul-sharma20/slack-standup/issues|issue tracker>."
        }
    ]
}


CONFIGURE_VIEW = {
    "type": "modal",
    "callback_id": "configure_standup",
    "submit": {
            "type": "plain_text",
        "text": "Submit",
                "emoji": True
    },
    "close": {
        "type": "plain_text",
        "text": "Cancel",
        "emoji": True
    },
    "title": {
        "type": "plain_text",
        "text": "Configure Standup",
        "emoji": True
    },
    "blocks": [
        {
            "type": "divider"
        },
        {
            "type": "input",
            "element": {
                "type": "multi_users_select",
                "action_id": "multi_users_select-action"
            },
            "label": {
                "type": "plain_text",
                "text": "Users",
                "emoji": True
            }
        },
        {
            "type": "input",
            "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "plain_text_input-action"
            },
            "label": {
                "type": "plain_text",
                "text": "Standup questions",
                "emoji": True
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Questions are new line separated"
                }
            ]
        },
        {"type": "divider"},
        {
            "type": "section",
            "block_id": "channels_select",
            "text": {
                "type": "mrkdwn",
                "text": "Channel where submissions will be published"
            },
            "accessory": {
                "type": "channels_select",
                "action_id": "channels_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select an item"
                }
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "block_id": "timepicker_select",
            "text": {
                "type": "mrkdwn",
                "text": "Time when submissions will be published"
            },
            "accessory": {
                "type": "timepicker",
                "initial_time": "13:00",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select time",
                    "emoji": True
                },
                "action_id": "timepicker_action"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Time in UTC"
                }
            ]
        }
    ]
}
