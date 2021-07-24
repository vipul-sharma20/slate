import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, \
    Enum, Time
from sqlalchemy.orm import relationship

from app import db


association_table = Table(
    "association",
    db.Model.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("team_id", Integer, ForeignKey("team.id")),
    extend_existing=True,
)


class PostSubmitActionEnum(enum.Enum):
    cat = 1
    dog = 2


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(String(20), unique=False)
    username = Column(String(50), unique=False)
    is_active = Column(Boolean, unique=False, default=True)
    submission = relationship(
        "Submission", lazy='dynamic', back_populates="user")
    team = relationship("Team", secondary=association_table,
                        back_populates="user")
    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=True)
    post_submit_action = Column(Enum(PostSubmitActionEnum), nullable=True)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Team(db.Model):
    __tablename__ = "team"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=True)
    standup = relationship("Standup", uselist=False, back_populates="team")
    user = relationship("User", secondary=association_table,
                        back_populates="team")
    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=True)


class Submission(db.Model):
    __tablename__ = "submission"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="submission")
    standup_id = Column(Integer, ForeignKey('standup.id'))
    standup = relationship("Standup")
    standup_submission = Column(String(), unique=False)
    created_at = Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Standup(db.Model):
    __tablename__ = "standup"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    standup_blocks = Column(String(), unique=False)
    trigger = Column(String(10), unique=False)
    is_active = Column(Boolean, unique=False, default=True)
    team_id = Column(Integer, ForeignKey("team.id"))
    team = relationship("Team", back_populates="standup")
    publish_channel = Column(String(20), unique=False)
    publish_time = Column(Time, nullable=True)
    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=True)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Auth(db.Model):
    __tablename__ = "auth"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user = Column(String(50), unique=False, nullable=True)
    token = Column(String(32), unique=False, nullable=True)
    is_active = Column(Boolean, unique=False, default=True, nullable=True)
    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=True)
