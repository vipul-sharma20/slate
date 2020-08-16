import json

from app.constants import (
    STANDUP_INFO_SECTION,
    STANDUP_USER_SECTION,
    STANDUP_SECTION_DIVIDER,
)


# Format standups in the Slack's block syntax
def build_standup(submissions) -> list:
    formatted_standup: dict = {}
    standup_user_section = STANDUP_USER_SECTION

    formatted_standup: list = []

    for submission in submissions:
        formatted_standup.append(STANDUP_INFO_SECTION)
        formatted_standup.append(STANDUP_SECTION_DIVIDER)

        standup_user_section["text"]["text"] = f"<@{submission.user_id}>"
        formatted_standup.append(standup_user_section)

        standup_json = json.loads(submission.standup_submission)
        blocks = standup_json.get("blocks", [])
        values = standup_json.get("state", {}).get("values", {})
        print(blocks)
        print(values)

        standup_content_section = {"type": "section", "fields": []}

        for block in blocks:
            block_id = block.get("block_id", "")
            action_id = block.get("element", {}).get("action_id", "")

            title = block.get("label", {}).get("text", "")
            content = values.get(block_id, {}).get(action_id, {}).get("value", "")

            standup_field = {"type": "mrkdwn", "text": f"*{title}*\n{content}"}
            standup_content_section["fields"].append(standup_field)
            print(standup_content_section)

        formatted_standup.append(standup_content_section)
        formatted_standup.append(STANDUP_SECTION_DIVIDER)
    return formatted_standup

