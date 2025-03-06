import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class Users(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, default='')
    name = sqlalchemy.Column(sqlalchemy.String, default='')
    mark = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    marked_articles = sqlalchemy.Column(sqlalchemy.String, default='{}')
    subscribed = sqlalchemy.Column(sqlalchemy.String, default='{}')
    reading = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    description = sqlalchemy.Column(sqlalchemy.String, default='')
    contacts = sqlalchemy.Column(sqlalchemy.String, default='')
    subscribers = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    articles = sqlalchemy.orm.relationship("Articles", back_populates='user')
    photo = sqlalchemy.Column(sqlalchemy.String, default='default_logo.jpg')

    def set_password(self, password: str) -> None:
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)
