### Deployment

```
helm install --name slack-standup . values.yaml
```

#### Configuring crons

Apply crons as below
```
kubectl apply -f crons/crons.yaml
```

These are crons for reminding teams for standup submissions and publishing
submissions on a Slack channel. Please edit commands, cron trigger time etc. in
`crons.yaml` before applying.
