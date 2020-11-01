from datetime import datetime

import pytz
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from . import db


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(20), unique=False)
    username = Column(String(50), unique=False)
    is_active = Column(Boolean, unique=False, default=True)
    submission = relationship(
        "Submission", lazy="dynamic", cascade="all, delete", passive_deletes=True
    )
    standup = relationship("Standup")
    standup_id = Column(Integer, ForeignKey("standup.id"))
    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=True)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Submission(db.Model):
    __tablename__ = "submission"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User")
    standup_submission = Column(String(), unique=False)
    created_at = Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Standup(db.Model):
    __tablename__ = "standup"
    id = Column(Integer, primary_key=True)
    standup_blocks = Column(String(), unique=False)
    trigger = Column(String(10), unique=False)
    is_active = Column(Boolean, unique=False, default=True)
    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=True)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Auth(db.Model):
    __tablename__ = "auth"
    id = Column(Integer, primary_key=True)
    user = Column(String(50), unique=False, nullable=True)
    token = Column(String(32), unique=False, nullable=True)
    is_active = Column(Boolean, unique=False, default=True, nullable=True)
    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=True)

