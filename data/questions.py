import datetime
import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase


class Questions(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    brand = sqlalchemy.Column(sqlalchemy.String)
    body = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_solved = sqlalchemy.Column(sqlalchemy.Boolean)
    mark = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    readings = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relationship('Users')