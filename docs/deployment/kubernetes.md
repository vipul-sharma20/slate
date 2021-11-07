---
layout: default
title: Kubernetes
parent: Options
grand_parent: Deployment
---

## Kubernetes

Deploy on an existing Kubernetes using the helm chart in the repository [here](https://github.com/vipul-sharma20/slate/tree/master/charts) like below.
 
```
helm install --name slack-standup . values.yaml
```

### Configuring k8s crons

Apply crons as below
```
kubectl apply -f crons/crons.yaml
```

These are crons for reminding teams for standup submissions and publishing
submissions on a Slack channel. Please edit commands, cron trigger time etc. in
`crons.yaml` before applying.

