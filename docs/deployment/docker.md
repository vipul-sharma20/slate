---
layout: default
title: Docker
parent: Deployment
---

## Docker

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

