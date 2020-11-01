import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

redis_client = redis.Redis(host='localhost', port=6379, db=0)


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import routes
        db.create_all()
        init_redis()
        print("started")

        return app


def init_redis():
    from app.models import Auth

    keys = Auth.query.all()

    for key in keys:
        if key.token and key.user:
            redis_client.set(key.token, key.user)

