import os

ALL = "all"
ACTIVE = "active"
INACTIVE = "inactive"

CAT_API_HOST = "https://api.thecatapi.com"

NO_USER_ERROR_MESSAGE = "Your user details or standup for your user doesn't exist in the database."

STANDUP_CHANNEL_ID = os.environ.get("STANDUP_CHANNEL_ID")

STANDUP_INFO_SECTION = {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "*Daily Standup Complete*"},
}

STANDUP_SECTION_DIVIDER = {"type": "divider"}

STANDUP_USER_SECTION = {"type": "section", "text": {"type": "mrkdwn", "text": ""}}


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
    "text": {"type": "mrkdwn", "text": "Thanks for submitting today's standup :slightly_smiling_face:"}
}


SUBMIT_TEMPLATE_SECTION_2 = {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "Here's a cat for you"}
}

