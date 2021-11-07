---
layout: default
title: Usage
nav_order: 5
---

# Usage

This page explains basic usage pattern of Slate.

---

## Creating new / editing existing standup

Use slash command `/standup configure` (or `/<your-configured-name> configure` in case you configure a different name when you install the app).

This will open a dialog box like below where you can:
- Add users you want in this standup.
- Set questions for the standup, each line separated.
- The channel where the standup submissions should be posted.
- The time at which the standup submissions should be posted.

This dialog box view looks like the screenshot below.

<h4 align="center">Standup configuration dialog box (new/existing)</h4>
<p align="center"><img src="https://i.imgur.com/Nf5c9ba.png" width="500px"/></p>

---

## Submitting standup

### Using slash command

Use slash command `/standup <team-name>` (or `/<your-configured-name> <team-name>` in case you
configure a different name when you install the app) to open up a dialog box
where you can submit your standup.

### Using pre-scheduled cron notifications

In case you schedule [crons][crons] for notifications, you'll get a Slack
notification like below.

<h4 align="center">Daily user notification for standup submission</h4>
<p align="center"><img src="https://i.imgur.com/x5Qrb7C.png" width="500px"/></p>

You can click on "Open Dialog" and submit your standup.

Screenshot of the dialog box is below.

<h4 align="center">Standup submission dialog box</h4>
<p align="center"><img src="https://i.imgur.com/mddlZb4.png" width="500px"/></p>

---

## Publishing standup

### Using pre-scheduled crons

Check the [crons][crons] to setup cron jobs for publishing standups. Published
crons on a Slack channel should look like below.

<h4 align="center">Standup publish view on channel (individual submissions in thread)</h4>
<p align="center"><img src="https://i.imgur.com/Evgomr9.png" width="500px"/></p>

Individual submission will be as messages in the thread.

---

## Editing standup

Once you submit your standup, you get a copy of your submission which you can
also edit it by clicking the "Edit" button.

Your copy of submission looks like below.

<h4 align="center">Submission view in DM</h4>
<p align="center"><img src="https://i.imgur.com/zUrqkyT.png" width="500px"/></p>


[crons]: ./deployment/crons.html
