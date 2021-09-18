
<p align="center"><img src="https://i.imgur.com/ndfRgcz.png" width="200px"/></p>

<div align="center">Self hosted Slack app for daily standups.</div>

![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/vipul-sharma20/slate?style=flat-square)

## Features

- Create standup submissions using Slack dialog box or slash commands.
- Ability to add different standup forms/questions for different teams.
- Notify users to submit their standups.
- Publish standup responses to a Slack channel. Can configure different Slack
  channels for different teams.
- CRUD APIs to manage standups, submissions, users, teams etc.


Check usage and API further in the README.

## Deployment

### Docker

```
docker-compose up
```

Pre-built image at: https://hub.docker.com/repository/docker/vipul20/slack-standup

Make sure to update the following environment variables in [`docker-compose.yml`](./docker-compose.yml)

#### Slack tokens

- `SLACK_SIGNING_SECRET`: Slack signing secret
- `SLACK_API_TOKEN`: Bot user oauth token.

#### Other application environment variables

- `SQLALCHEMY_DATABASE_URI`: URI of the database to use. By default, a Sqlite DB is configured.


### Helm

Helm chart in [`./charts`](./charts) directory.

## Setting up the application on Slack

You can setup the Slack app using the app manifest (the easier way) or manually.

### Using app manifest

Create a new app on Slack and import the [`app_manifest.yml`](./app_manifest.yml) configuration.

Make sure to update the following configs:

- `url`: update host and port with the your deployment
- `request_url`: update host and port with the your deployment

Change any other information based on your preference for eg: slash commands etc.

### Manual

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


*Note: Anything below this is outdated. It's being updated as a part of: https://github.com/vipul-sharma20/slack-standup/issues/14*

## Screenshots

<p align="center">
    <b>Slash command</b><br/><br/>
    <img src="https://i.imgur.com/LYXXTax.png" />
</p>

---

<p align="center">
    <b>Standup form</b><br/><br/>
    <img src="https://i.imgur.com/XemSNPf.png" />
</p>

---

<p align="center">
    <b>Reporting submissions on the channel</b><br/><br/>
    <img src="https://i.imgur.com/Ns4YLd2.png" />
</p>

---

<p align="center">
    <b>User standup notification</b><br/><br/>
    <img src="https://i.imgur.com/V6kxTCS.png" />
</p>


## Usage

Use the slash command to trigger with the standup you want to fill

`/standup <team-name>`

This will open any standup which is added for the user who triggered it

Alternatively you can also configure user DM notifications which will allow
them to open form from the notification message. Check API below in
"Notifications and Reporting" section

## API

There are APIs to fetch, create, update and delete users, standup forms, user
submissions over a date range etc.. These can be used to integrate with a UI
application.

API usage, examples and doc at: [https://www.getpostman.com/collections/4e76e0951616b3df4e5f][3]

## DB

This application uses SQLite DB which can be replaced with any other DB by the
users of this repo. I am using SQLAlchemy as the ORM.

## Notifications and Reporting

* Currently, there's a single GET API endpoint which can be scheduled as a cron
  to report all the submitted standups in a channel: `/slack/publish_standup/`
* You can notify users to submit standup by hitting the `/slack/notify_usesrs/`
  endpoint. It will send DMs to people who have not submitted the standup
  (check screenshot above).

## License

MIT


[0]: https://i.imgur.com/LYXXTax.png
[1]: https://i.imgur.com/XemSNPf.png
[2]: https://i.imgur.com/Ns4YLd2.png
[3]: https://www.getpostman.com/collections/4e76e0951616b3df4e5f
[4]: https://api.slack.com/surfaces#modals
[5]: https://bit.ly/340PukR
[6]: https://i.imgur.com/l94Tg4U.png
[7]: https://github.com/vipul-sharma20/slack-standup/releases/tag/v0.3-beta
