---
layout: default
title: Crons
nav_order: 2
parent: Deployment
---

Slate provides APIs to notify users, publish standup to Slack etc. One way to
schedule these notifications and publishing time is via crons.

To publish standup submissions you can use the following approach:
- Kubernetes crons (in case you went with K8s based installation).
- Calling publish standup API via a cron or manually to publish to Slack
  channel.
  
## Kubernetes crons

Follow the doc [here][k8s-crons] to setup required crons for Kubernetes cluster
deployment.

## Generic crons

### 1. Cron to notify users

```bash
30 7 * * 1-5 curl --location --request GET 'https://<host>/api/notify_users/<team-name>/' --header 'Authorization: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

This will set a cron to notify users every Monday to Friday at 7:30 UTC.

### 2. Cron to publish standup submissions

```bash
30 8 * * 1-5 curl --location --request GET 'https://<host>/slack/publish_standup/<team-name>/' --header 'Authorization: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

This will publish all the standup submissions every Monday to Friday at 8:30
UTC to the Slack channel configured.

[k8s-crons]: ./kubernetes.html#configuring-k8s-crons
