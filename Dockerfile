FROM python:3.8

WORKDIR /home/slack-standup/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /home/slack-standup/

ENV SLACK_SIGNING_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ENV SLACK_API_TOKEN=xoxb-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ENV SQLALCHEMY_DATABASE_URI="sqlite:////Users/vipul/submission.db"
ENV STANDUP_CHANNEL_ID="C0XXXXXXXXX"
ENV FLASK_APP=app

CMD ["uwsgi", "--http-socket", ":5000", "--module", "\"app:create_app()\"", "--workers", "4"]

# docker run -p 5000:5000 -v ~/itandup.db:/home/slack-standup/standup.db -e SQLALCHEMY_DATABASE_URI=sqlite:////home/slack-standup/standup.db -e STANDUP_CHANNEL=C0XXXXXXXXX -e SLACK_API_TOKEN=xoxb-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX -e SLACK_SIGNING_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX -i -t standup
