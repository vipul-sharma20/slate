---
layout: default
title: Development
nav_order: 4
permalink: docs/development
---

# Development

Follow the steps below to setup this project for development.

## Setup dependencies

- This project works on Python3.8+
- Install required packages
```
pip install -r requirements.txt
```

## Starting development server

### Export essential environment variables

- `SLACK_SIGNING_SECRET`: Slack signing secret
- `SLACK_API_TOKEN`: Bot user oauth token.
- `SQLALCHEMY_DATABASE_URI`: URI of the database to use. By default, a Sqlite DB is configured.
- `FLASK_APP=app`:

### DB setup

```
flask db stamp head
flask db migrate
flask db upgrade
```

### Start server

```
flask run --host 0.0.0.0 --port 5000
```

## Install on Slack

To test this development deployment, install this to your Slack workspace by following the doc [here](./Installation).

You can expose the local server via [ngrok](https://ngrok.com/) for test purposes like below
```
ngrok http 5000
```


