from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean

from . import db


class Submission(db.Model):
    __tablename__ = 'submission'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(20), unique=False)
    username = Column(String(50), unique=False)
    standup_submission = Column(String(), unique=False)
    created_at = Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Standup(db.Model):
    __tablename__ = "standup"
    id = Column(Integer, primary_key=True)
    standup_blocks = Column(String(), unique=False)
    trigger = Column(String(10), unique=False)
    is_active = Column(Boolean, unique=False, default=True)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
