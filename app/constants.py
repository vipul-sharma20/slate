import os


STANDUP_CHANNEL_ID = os.environ.get("STANDUP_CHANNEL_ID")

STANDUP_INFO_SECTION = {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "*Daily Standup Complete*"},
}

STANDUP_SECTION_DIVIDER = {"type": "divider"}

STANDUP_USER_SECTION = {"type": "section", "text": {"type": "mrkdwn", "text": ""}}


ALL = "all"
ACTIVE = "active"
INACTIVE = "inactive"
