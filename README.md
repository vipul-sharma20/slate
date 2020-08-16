# slack-standup

An application for Slack based standups. This is a Flask server application to
handle Slack callbacks, create/submit standups, report to a channel etc.

Check usage and API further in the README.

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

## Configuration

* Create a new standup app in your Slack workspace
* Generate tokens and secrets
* Create slash command to trigger the modal (eg: `/standup`)
* Configure the HTTP URL for the slash command to: `http://127.0.0.0:5000/slack/standup-trigger/`. Replace `127.0.0.1:5000` with your deployment host/port.
* Add HTTP URL in the "Interactivity & Shortcuts" to handle the form submission.
    * Enable "Interactivity"
    * URL: `http://127.0.0.1:5000/slack/submit_standup/`. Replace `127.0.0.1:5000` with your deployment host/port.

Some environment variables for the application:

```bash
export SLACK_API_TOKEN="<slack-api-token-here>"
export SLACK_SIGNING_SECRET="<slack-signing-secret-here>"
export SQLALCHEMY_DATABASE_URI="sqlite:////path/to/standup.db"
export STANDUP_CHANNEL_ID="C0XXXXXXXXX"  # Channel where submissions will be posted
```

### Docker

`docker build . -t slack-standup`

or

`docker pull vipul20/slack-standup:latest`

Check Dockerfile for help with run command

## Standup Form / Modal

The Slack form/modal can be built using the Block Kit Builder.

Block Kit is a UI framework for Slack apps that offers a balance of control and
flexibility when building experiences in messages and other surfaces (I am
using [modal][4] here)

Using the Block Kit Builder you can create any modal you like and add the JSON
data generated as a standup using the APIs (doc below). The application will
fetch all the blocks used in the modal and display it appropriately while
publishing to a channel.

Block Kit sample shown in screenshot can be found here: [https://bit.ly/340PukR][5]
Screenshot for the same Block Kit sample is [here][6]

## Usage

Use the slash command to trigger with the standup you want to fill

`/standup engg`

This will open any standup which is added for `engg`

## DB

This application uses SQLite DB which can be replaced with any other DB by the
users of this repo. I am using SQLAlchemy as the ORM.

* Standup table has:
    * `standup_blocks`: Blocks for the Slack modal
    * `trigger`: Trigger word for this standup (eg: `engg`)
    * `is_active`: Whether the standup is active or not

* Submission table has:
    * `user_id`: Slack user id of submitter
    * `username`: Slack username of the submitter
    * `standup_submission`: The standup content submitted

## API

There are APIs to fetch, create, update and delete standup forms. These can be
used to integrate with a UI application.

For API usage and examples, please check the Postman [collection][3]

## Reporting

Currently, there's a single GET API endpoint which can be scheduled as a cron
to report all the submitted standups in a channel: `/slack/publish_standup/`

## License

MIT

## TODO

Some TODOs/scribbles on what can be a few good features:

- [ ] A UI to fetch, create, update and delete standup (Would appreciate any
  contribution here :))
- [ ] Feature to assign users to standups rather than users choosing a standup
  from the slash command
- [ ] ...


[0]: https://i.imgur.com/LYXXTax.png
[1]: https://i.imgur.com/XemSNPf.png
[2]: https://i.imgur.com/Ns4YLd2.png
[3]: https://www.getpostman.com/collections/c179a577fde7b13229f4
[4]: https://api.slack.com/surfaces#modals
[5]: https://bit.ly/340PukR
[6]: https://i.imgur.com/l94Tg4U.png
