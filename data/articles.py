from typing import Type
from data import users, comments, db_session
from sqlalchemy import desc, and_
from flask import *
import json
import datetime
import sqlalchemy
from werkzeug.utils import secure_filename
import os
from server import app
from forms.ArticleForm import *
from users import Users, current_user


class Articles(db_session.SqlAlchemyBase):
    __tablename__ = 'articles'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    categories = sqlalchemy.Column(sqlalchemy.String)
    describe = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    mark = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    photo = sqlalchemy.Column(sqlalchemy.String)
    readings = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = sqlalchemy.orm.relationship('User')


class Article:
    def __init__(self):
        self.db_sess = db_session.create_session()

    def add(self, text: str, form: CreatingArticleDataForm, user: Users) -> None:
        text = text.replace('<img', '<img height="100%" width="100%"')
        article = Articles(text=text, user_id=user.id, created_date=datetime.datetime.now(),
                           brand=form.brand_category.data, body=form.body_category.data,
                           motors=form.motors_category.data, price_from=form.price_from.data,
                           price_to=form.price_to.data, name=form.name.data, describe=form.describe.data,
                           categories=form.category.data)
        file = form.photo.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        article.photo = filename
        self.db_sess.add(article)
        self.db_sess.commit()

    def getCategory(self, category: str = None) -> list:
        if category is None:
            return self.db_sess.query(Articles).filter(
                Articles.created_date.ilike('%' + f'{datetime.datetime.today().date()}' + '%')).order_by(
                desc(Articles.readings)).all()
        categories = {'tops': 'Топ', 'reviews': 'Обзоры', 'comparisons': 'Сравнения'}
        return self.db_sess.query(Articles).filter(and_(
            Articles.created_date.ilike('%' + str(datetime.datetime.today().date()) + '%'),
            Articles.categories == categories[category])).order_by(
            desc(Articles.readings)).all()

    def getSubscribed(self, user: Users) -> list:
        all_subs = [int(i) for i, k in json.loads(user.subscribed).items() if k == '1']
        return self.db_sess.query(Articles).filter(and_(
            Articles.created_date.ilike('%' + str(datetime.datetime.today().date()) + '%'),
            Articles.user_id.in_(all_subs))).order_by(
            desc(Articles.readings)).all()

    def getOnUser(self, user_id: Users.id) -> list:
        return self.db_sess.query(Articles).filter(Articles.user_id == user_id).all()

    def getData(self, all_articles: list) -> dict:
        data = {}
        for article in all_articles:
            creator = self.db_sess.query(users.Users).filter(users.Users.id == article.user_id).first()
            time = text_delta(datetime.datetime.now() - article.created_date)
            data[str(article.id)] = (creator.name, creator.photo, creator.subscribers, time, len(
                self.db_sess.query(comments.Comment).filter(comments.Comment.article_id == article.id).all()))
        return data

    def clicked(self) -> Response | None:
        to_read = request.form.get('id')
        to_delete = request.form.get('delete')
        if to_read:
            self.read(to_read)
            return redirect(f'/article/{to_read}/read')
        elif to_delete:
            self.db_sess.query(Articles).filter(Articles.id == to_delete).delete()
            self.db_sess.commit()

    def read(self, id_article: Articles.id) -> None:
        article = self.get(id_article)
        article.readings += 1
        user = self.db_sess.query(users.Users).filter(users.Users.id == article.user_id).first()
        user.reading += 1
        self.db_sess.commit()

    def find(self, text: str) -> list:
        return self.db_sess.query(Articles).filter(Articles.name.ilike('%' + text + '%')).order_by(
            desc(Articles.readings)).all()

    def get(self, article_id: Articles.id) -> Type[Articles]:
        return self.db_sess.query(Articles).filter(Articles.id == article_id).first()

    def addMark(self, article_id: Articles.id, mark: int) -> None:
        article = self.get(article_id)
        user = users.User().get(current_user.id)
        author = users.User().get(article.user_id)
        prev_mark = json.loads(user.marked_articles)
        if (not prev_mark) or (not str(article_id) in prev_mark.keys()):
            article.mark += mark
            author.mark += mark
            prev_mark[str(article_id)] = str(mark)
        elif 1 >= int(prev_mark[str(article_id)]) + mark >= -1:
            article.mark += (mark - int(prev_mark[str(article_id)]))
            author.mark += (mark - int(prev_mark[str(article_id)]))
            prev_mark[str(article_id)] = str(mark)
        elif not 1 >= int(prev_mark[str(article_id)]) + mark >= -1:
            article.mark -= mark
            author.mark -= mark
            prev_mark[str(article_id)] = '0'
        user.marked_articles = json.dumps(prev_mark)
        self.db_sess.commit()

    def getFollowed(self, user_id: Users.id) -> list:
        user = users.User().get(user_id)
        return [self.get(int(i)) for i, k in json.loads(user.marked_articles).items() if k == '1']


def text_delta(t: datetime) -> str:
    if t < datetime.timedelta(minutes=1):
        return "Минуту назад"
    elif t < datetime.timedelta(hours=1):
        return f"{t.total_seconds() // 60:.0f} минут назад"
    elif t < datetime.timedelta(days=1):
        return f"{t.total_seconds() // 3600:.0f} часов назад"
    elif t < datetime.timedelta(days=30):
        return f"{t.days} дней назад"
    elif t < datetime.timedelta(days=365):
        return f"{t.days // 30} месяцев назад"
    else:
        return f"{t.days // 365} лет назад"
