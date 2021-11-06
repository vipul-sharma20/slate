---
layout: default
title: Manual
parent: Installation
---

## Manual

- Create an app on Slack, for example: `slack-standup`.
- Create Slack bot token (check "OAuth & Permissions" in your app page) and add
  it as environment variable in [`docker-compose.yml`](./docker-compose.yml).
    - Add following scopes: `channels:history`, `chat:write`, `commands`,
      `users:read`.
- Deploy the application with the tokens.
- Under "Interactivity & Shortcuts" option, add request URL as
  `host:port/slack/submit_standup/`
- Add a slash command using the "Slash Commands" option.
    - Use request URL as `host:port/slack/standup-trigger/`
- Add the Slack app in your channel (Example: `/invite @slack-doc`).
