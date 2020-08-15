import os


STANDUP_CHANNEL_ID = os.environ.get("STANDUP_CHANNEL_ID")

STANDUP_MODAL_TEMPLATE = {
    "type": "modal",
    "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
    "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
    "title": {"type": "plain_text", "text": "Workplace check-in", "emoji": True},
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": ":wave: Hey David!\n\nWe'd love to hear from you how we can make this place the best place you’ve ever worked.",
                "emoji": True,
            },
        },
        {"type": "divider"},
        {
            "type": "input",
            "label": {
                "type": "plain_text",
                "text": "What do you want for our team weekly lunch?",
                "emoji": True,
            },
            "element": {
                "type": "multi_static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select your favorites",
                    "emoji": True,
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": ":pizza: Pizza",
                            "emoji": True,
                        },
                        "value": "value-0",
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": ":fried_shrimp: Thai food",
                            "emoji": True,
                        },
                        "value": "value-1",
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": ":desert_island: Hawaiian",
                            "emoji": True,
                        },
                        "value": "value-2",
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": ":meat_on_bone: Texas BBQ",
                            "emoji": True,
                        },
                        "value": "value-3",
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": ":hamburger: Burger",
                            "emoji": True,
                        },
                        "value": "value-4",
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": ":taco: Tacos",
                            "emoji": True,
                        },
                        "value": "value-5",
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": ":green_salad: Salad",
                            "emoji": True,
                        },
                        "value": "value-6",
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": ":stew: Indian",
                            "emoji": True,
                        },
                        "value": "value-7",
                    },
                ],
            },
        },
        {
            "type": "input",
            "label": {
                "type": "plain_text",
                "text": "What can we do to improve your experience working here?",
                "emoji": True,
            },
            "element": {"type": "plain_text_input", "multiline": True},
        },
        {
            "type": "input",
            "label": {
                "type": "plain_text",
                "text": "Anything else you want to tell us?",
                "emoji": True,
            },
            "element": {"type": "plain_text_input", "multiline": True},
            "optional": True,
        },
    ],
}


STANDUP_MODAL_TEMPLATE = {
    "type": "modal",
    "callback_id": "modal-identifier",
    "title": {"type": "plain_text", "text": "New Post"},
    "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
    "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
    "blocks": [
        {
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "action_id": "title",
                "placeholder": {"type": "plain_text", "text": "Input title"},
            },
            "label": {"type": "plain_text", "text": "Title"},
        },
        {
            "type": "input",
            "element": {"type": "plain_text_input", "multiline": True},
            "label": {"type": "plain_text", "text": "Content", "emoji": True},
        },
    ],
}


STANDUP_INFO_SECTION = {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "*Daily Standup Complete*"},
}

STANDUP_SECTION_DIVIDER = {"type": "divider"}

STANDUP_USER_SECTION = {"type": "section", "text": {"type": "mrkdwn", "text": ""}}

