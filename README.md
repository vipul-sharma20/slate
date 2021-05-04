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

---

<p align="center">
    <b>User standup notification</b><br/><br/>
    <img src="https://i.imgur.com/V6kxTCS.png" />
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

## Docker

`docker-compose up`

Note: update the environment variables in the `docker-compose.yml` file

## Usage

Use the slash command to trigger with the standup you want to fill

`/standup`

This will open any standup which is added for the user who triggered it

Alternatively you can also configure user DM notifications which will allow
them to open form from the notification message. Check API below in
"Notifications and Reporting" section

## API

There are APIs to fetch, create, update and delete users, standup forms, user
submissions over a date range etc.. These can be used to integrate with a UI
application.

API usage, examples and doc at: [https://documenter.getpostman.com/view/803934/TVYKbwpd][3]

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
[3]: https://documenter.getpostman.com/view/803934/TVYKbwpd
[4]: https://api.slack.com/surfaces#modals
[5]: https://bit.ly/340PukR
[6]: https://i.imgur.com/l94Tg4U.png
[7]: https://github.com/vipul-sharma20/slack-standup/releases/tag/v0.3-beta
