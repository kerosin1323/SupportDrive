from data import db_session
import datetime
import sqlalchemy


class Answers(db_session.SqlAlchemyBase):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_right = sqlalchemy.Column(sqlalchemy.Boolean)
    text = sqlalchemy.Column(sqlalchemy.String)
    mark = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    level = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    question_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('questions.id'))
    article = sqlalchemy.orm.relationship('Questions')