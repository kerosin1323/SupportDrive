from server import db_session
from data import articles, users, comments
from sqlalchemy import desc, and_
from flask_login import *
from flask import *
import datetime
from data.SQL_functions import *
from forms.UserForm import *
from forms.ArticleForm import *


def getMostPopularArticle(category=None):
    db_sess = db_session.create_session()
    if category is None:
        return db_sess.query(articles.Articles).filter(
            articles.Articles.created_date.ilike('%' + f'{datetime.datetime.today().date()}' + '%')).order_by(
            desc(articles.Articles.readings))
    elif category == 'subscribed' and current_user.is_authenticated and current_user.subscribed:
        getSubscribed()
    elif category != 'subscribed':
        categories = {'tops': 'Топ', 'reviews': 'Обзоры', 'comparisons': 'Сравнения'}
        return db_sess.query(articles.Articles).filter(and_(
            articles.Articles.created_date.ilike('%' + str(datetime.datetime.today().date()) + '%'),
            articles.Articles.categories == categories[category])).order_by(
            desc(articles.Articles.readings)).all()
    return []

def getSubscribed():
    db_sess = db_session.create_session()
    all_subs = [int(i) for i, k in json.loads(current_user.subscribed).items() if k == '1']
    return db_sess.query(articles.Articles).filter(and_(
        articles.Articles.created_date.ilike('%' + str(datetime.datetime.today().date()) + '%'),
        articles.Articles.user_id.in_(all_subs))).order_by(
        desc(articles.Articles.readings)).all()


def checkToDelete():
    db_sess = db_session.create_session()
    to_delete = request.form.get('delete')
    if to_delete:
        db_sess.query(articles.Articles).filter(articles.Articles.id == to_delete).delete()
        db_sess.commit()


def text_delta(t) -> str:
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


def getArticleData(all_articles):
    db_sess = db_session.create_session()
    data = {}
    for article in all_articles:
        creator = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
        time = text_delta(datetime.datetime.now() - article.created_date)
        data[str(article.id)] = (creator.name, creator.photo, creator.subscribers, time, len(
            db_sess.query(comments.Comment).filter(comments.Comment.article_id == article.id).all()))
    return data


def clickedOnArticle():
    id_article = request.form.get('id')
    if id_article:
        ReadingArticle(id_article)
        return redirect(f'/article/{id_article}/read')


def createUser():
    form = RegisterForm()
    db_sess = db_session.create_session()
    user = users.User(name=form.username.data, login=form.login.data)
    user.set_password(form.password.data)
    db_sess.add(user)
    db_sess.commit()
    login_user(user)


def userAlreadyExist(login):
    db_sess = db_session.create_session()
    return bool(len(db_sess.query(users.User).filter(users.User.login == login).all()))


def checkAndLoginUser(name, password):
    db_sess = db_session.create_session()
    user = db_sess.query(users.User).filter(users.User.name == name).first()
    if user and user.check_password(password):
        login_user(user)
        return redirect("/")