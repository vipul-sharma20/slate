FROM python:3.8

WORKDIR /home/slack-standup/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /home/slack-standup/

ENV SLACK_SIGNING_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ENV SLACK_API_TOKEN=xoxb-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ENV SQLALCHEMY_DATABASE_URI="sqlite:////home/slack-standup/standup.db"
ENV FLASK_APP=app
ENV REDIS_HOST=localhost
ENV REDIS_PORT=6379
ENV ENVIRONMENT=PROD

RUN flask db stamp head
RUN flask db migrate
RUN flask db upgrade

CMD ["uwsgi", "--http-socket", ":5000", "--enable-threads", "--threads", "4", "--module", "app:create_app()", "--workers", "2", "--buffer-size", "32768"]

# docker run -p 5000:5000 -e SQLALCHEMY_DATABASE_URI=sqlite:////home/slack-standup/standup.db -e STANDUP_CHANNEL_ID=C0XXXXXXXXX -e SLACK_API_TOKEN=xoxb-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX -e SLACK_SIGNING_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX -i -t standup

