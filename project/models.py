from datetime import datetime
from flask_login import UserMixin
from enum import Enum
from . import db

class Role(str, Enum):
    USER = "User"
    ADMIN = "Administrator"

class ContainerRole(str, Enum):
    READER = "Reader"
    EDITOR = "Editor"

class ContainerType(str, Enum):
    REGULAR = "Regular"
    GUEST = "Guest"


class UserContainer(db.Model):
    __tablename__ = 'user_container'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    container_id = db.Column(db.String(100), db.ForeignKey('container.id'), primary_key=True)
    container_role = db.Column(db.Enum(ContainerRole), default=ContainerRole.READER)
    user = db.relationship('User', back_populates='container_links')
    container = db.relationship('Container', back_populates='user_links')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    role = db.Column(db.Enum(Role), default=Role.USER)
    container_links = db.relationship('UserContainer', back_populates='user', cascade="all, delete-orphan")

class Container(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    port = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    container_name = db.Column(db.String(100))
    container_type = db.Column(db.Enum(ContainerType), default=ContainerType.REGULAR)
    user_links = db.relationship('UserContainer', back_populates='container', cascade="all, delete-orphan")