from data import users, articles, db_session, comments
from sqlalchemy import desc
from flask import *
from typing import NamedTuple, Type
import json
import datetime
from werkzeug.utils import secure_filename
import os
from forms.ArticleForm import *
from forms.UserForm import *
from flask_login import *
from data.users import Users
from mailing import send_simple_email
from random import randint

db_session.global_init("db/blogs.sql")
db_sess = db_session.create_session()


class TopArticle(NamedTuple):
    tops: Type[articles.Articles]
    reviews: Type[articles.Articles]
    comparisons: Type[articles.Articles]
    news: Type[articles.Articles]


def create_article(text: str, form: CreatingArticleDataForm, user_id: Users.id, app) -> None:
    text = text.replace('<img', '<img height="100%" width="100%"')
    article = articles.Articles(text=text, user_id=user_id, created_date=datetime.datetime.now(),
                                brand=form.brand_category.data, body=form.body_category.data,
                                motors=form.motors_category.data, price_from=form.price_from.data,
                                price_to=form.price_to.data, name=form.name.data, describe=form.describe.data,
                                categories=form.category.data)
    add_photo(form.photo.data, article, app)
    db_sess.add(article)
    db_sess.commit()


def add_photo(file, article, app) -> None:
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        article.photo = filename


def get_on_category(category: str = None) -> list[Type[articles.Articles]]:
    if category is None:
        return db_sess.query(articles.Articles).all()[::-1][:20]
    elif category == 'subscribed' and current_user.is_authenticated:
        get_article_subscribed(current_user)
    elif category != 'subscribed':
        categories = {'tops': 'Топ', 'reviews': 'Обзоры', 'comparisons': 'Сравнения', 'news': 'Новости'}
        return db_sess.query(articles.Articles).filter(articles.Articles.categories == categories[category]).all()[
               ::-1][:20]
    return []


def get_top() -> TopArticle:
    tops = db_sess.query(articles.Articles).filter(articles.Articles.categories == 'Топ').order_by(
        desc(articles.Articles.readings)).first()
    reviews = db_sess.query(articles.Articles).filter(articles.Articles.categories == 'Обзоры').order_by(
        desc(articles.Articles.readings)).first()
    comparisons = db_sess.query(articles.Articles).filter(articles.Articles.categories == 'Сравнения').order_by(
        desc(articles.Articles.readings)).first()
    news = db_sess.query(articles.Articles).filter(articles.Articles.categories == 'Новости').order_by(
        desc(articles.Articles.readings)).first()
    if tops and reviews and comparisons and news:
        return TopArticle(tops=tops, reviews=reviews, comparisons=comparisons, news=news)


def get_article_subscribed(user: Users) -> list[Type[articles.Articles]]:
    all_subs = [int(i) for i, k in json.loads(user.subscribed).items() if k == '1']
    return db_sess.query(articles.Articles).filter(articles.Articles.user_id.in_(all_subs)).all()


def get_article_from_user(user_id: Users.id) -> list[Type[articles.Articles]]:
    return db_sess.query(articles.Articles).filter(articles.Articles.user_id == user_id).all()


def get_article_data(all_articles: list[Type[articles.Articles]]) -> dict:
    data = {}
    for article in all_articles:
        creator = get_user(article.user_id)
        time = text_delta(datetime.datetime.now() - article.created_date)
        data[str(article.id)] = (creator.name, creator.photo, creator.subscribers, time, len(get_comments(article.id)))
    return data


def delete(article_id) -> None:
    db_sess.query(articles.Articles).filter(articles.Articles.id == article_id).delete()
    db_sess.commit()


def add_reading(id_article: articles.Articles.id) -> None:
    article = get_article(id_article)
    article.readings += 1
    user = get_user(article.user_id)
    user.reading += 1
    db_sess.commit()


def find(text: str) -> list:
    return db_sess.query(articles.Articles).filter(articles.Articles.name.ilike('%' + text + '%')).order_by(
        desc(articles.Articles.readings)).all()


def get_article(article_id: articles.Articles.id) -> Type[articles.Articles]:
    return db_sess.query(articles.Articles).filter(articles.Articles.id == article_id).first()


def mark_article(article_id: articles.Articles.id, mark: int) -> None:
    article = get_user(article_id)
    user = get_user(current_user.id)
    author = get_user(article.user_id)
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
    db_sess.commit()


def get_followed(user_id: Users.id) -> list:
    user = get_user(user_id)
    return [get_article(int(i)) for i, k in json.loads(user.marked_articles).items() if k == '1']


def text_delta(t: datetime) -> str:
    if t < datetime.timedelta(minutes=2):
        return "1 минуту назад"
    elif t < datetime.timedelta(hours=1):
        if t.total_seconds() // 60 % 10 in (2, 3, 4) and (t.total_seconds() // 60 > 20 or t.total_seconds() // 60 < 5):
            return f"{t.total_seconds() // 60:.0f} минуты назад"
        elif t.total_seconds() // 60 % 10 == 1 and (t.total_seconds() // 60 > 20 or t.total_seconds() // 60 < 5):
            return f"{t.total_seconds() // 60:.0f} минуту назад"
        else:
            return f"{t.total_seconds() // 60:.0f} минут назад"
    elif t < datetime.timedelta(days=1):
        if t.total_seconds() // 3600 % 10 in (2, 3, 4) and (
                t.total_seconds() // 3600 > 20 or t.total_seconds() // 3600 < 5):
            return f"{t.total_seconds() // 3600:.0f} часа назад"
        elif t.total_seconds() // 3600 % 10 == 1 and (t.total_seconds() // 3600 > 20 or t.total_seconds() // 3600 < 5):
            return f"{t.total_seconds() // 3600:.0f} час назад"
        else:
            return f"{t.total_seconds() // 3600:.0f} часов назад"
    elif t < datetime.timedelta(days=30):
        if t.days % 10 in (2, 3, 4) and (t.days > 20 or t.days < 5):
            return f"{t.days:.0f} дня назад"
        elif t.days % 10 == 1 and (t.days > 20 or t.days < 5):
            return f"{t.days:.0f} день назад"
        else:
            return f"{t.days:.0f} дней назад"
    elif t < datetime.timedelta(days=365):
        if t.days // 30 % 10 in (2, 3, 4) and (t.days // 30 > 20 or t.days < 5):
            return f"{t.days // 30:.0f} месяца назад"
        elif t.days // 30 % 10 == 1 and (t.days // 30 > 20 or t.days // 30 < 5):
            return f"{t.days // 30:.0f} месяц назад"
        else:
            return f"{t.days // 30:.0f} месяцев назад"
    else:
        if t.days // 365 % 10 in (2, 3, 4) and (t.days // 365 > 20 or t.days // 365 < 5):
            return f"{t.days // 365:.0f} года назад"
        elif t.days // 365 % 10 == 1 and (t.days // 365 > 20 or t.days // 365 < 5):
            return f"{t.days // 365:.0f} год назад"
        else:
            return f"{t.days // 365:.0f} лет назад"


def create_user(data: dict) -> None:
    user = Users(name=data['username'], email=data['email'])
    user.set_password(data['password'])
    db_sess.add(user)
    db_sess.commit()
    login_user(user)


def add_user_data(form: DescriptionProfile, user_id: Users.id, app: Flask) -> None:
    user = get_user(user_id)
    user.name = form.name.data
    add_photo(form.photo.data, user, app)
    user.description = form.description.data
    user.contacts = form.contacts.data
    db_sess.commit()


def get_user(user_id: Users.id) -> Type[Users]:
    return db_sess.query(Users).filter(Users.id == user_id).first()


def is_email_already_exist(email: str) -> bool:
    return bool(len(db_sess.query(Users).filter(Users.email == email).all()))


def check(email: str, password: str) -> bool:
    user = get_on_email(email)
    return user and user.check_password(password)


def send_password(email):
    password = randint(100000, 999999)
    send_simple_email(receiver_email=email, body=str(password))
    return password


def check_email_and_login_user(prev_link, password, email):
    parse_password = session[email][1]
    print(password, parse_password)
    if str(password) == str(parse_password):
        if prev_link == 'reg':
            create_user(session[email][0])
        else:
            user_log = get_on_email(email)
            login_user(user_log)
        return 'True'
    return 'Неправильный пароль'

def get_on_email(email: str):
    return db_sess.query(Users).filter(Users.email == email).first()


def get_leaders() -> list | None:
    leaders = db_sess.query(Users).order_by(desc(Users.mark)).all()[:5]
    if len(leaders) > 4:
        return leaders


def get_subscriptions(user_id: Users.id) -> list:
    user = get_user(user_id)
    if user.subscribed:
        return [get_user(int(i)) for i, k in json.loads(user.subscribed).items() if k == '1']


def subscribe(user_id: Users.id) -> None:
    user = get_user(current_user.id)
    author = get_user(user_id)
    prev_subs = json.loads(user.subscribed)
    if (not prev_subs) or (str(user_id) not in prev_subs) or (prev_subs[str(user_id)] == '0'):
        author.subscribers += 1
        prev_subs[str(user_id)] = '1'
    elif prev_subs[str(user_id)] == '1':
        author.subscribers -= 1
        prev_subs[str(user_id)] = '0'
    user.subscribed = json.dumps(prev_subs)
    db_sess.commit()


def check_subscribe(user_id: Users.id) -> bool | None:
    try:
        user = get_user(current_user.id)
    except Exception:
        return None
    if user.subscribed:
        return str(user_id) in [str(i) for i, k in json.loads(user.subscribed).items() if k == '1']


def check_for_admin(form) -> bool:
    user = db_sess.query(Users).filter(Users.name == form.name.data).first()
    if user and user.check_password(form.password.data):
        if user.subscribed > 100 and user.reading > 1000 and user.mark > 500:
            return True
    return False


def get_comments(article_id: articles.Articles.id) -> list:
    all_sorted_comments = []
    last_id_comment = len(db_sess.query(comments.Comments).order_by(desc(comments.Comments.mark)).filter(comments.Comments.article_id == article_id).all())
    id_comment = 1
    while id_comment <= last_id_comment != 0:
        current_comment = get_comment(id_comment)
        answers_on_current_comment = get_answers(id_comment)
        if current_comment in all_sorted_comments and len(answers_on_current_comment) != 0:
            idx_in_asc = all_sorted_comments.index(current_comment)
            all_sorted_comments = [*all_sorted_comments[:idx_in_asc], current_comment, *answers_on_current_comment, *all_sorted_comments[idx_in_asc+1:]]
        elif current_comment not in all_sorted_comments:
            if answers_on_current_comment != 0:
                all_sorted_comments += current_comment, *answers_on_current_comment
            else:
                all_sorted_comments += current_comment
        id_comment += 1
    return all_sorted_comments


def get_comment_data(all_comments: list) -> dict:
    data = {}
    for comment in all_comments:
        creator = get_user(comment.user_id)
        time = text_delta(datetime.datetime.now() - comment.created_date)
        data[str(comment.id)] = (creator.name, creator.photo, creator.subscribers, time)
    return data


def mark_comment(comment_id: comments.Comments.id, mark: int) -> None:
    comment = db_sess.query(comments.Comments).filter(comments.Comments.id == comment_id).first()
    if f'{current_user.id}' not in session or 'comments' not in session[str(current_user.id)] or str(
            comment_id) not in session[f'{current_user.id}']['comments']:
        comment.mark += mark
        session[f'{current_user.id}'] = {'comments': {f'{comment_id}': mark}}
    elif 1 >= int(session[f'{current_user.id}']['comments'][str(comment_id)]) + int(mark) >= -1:
        comment.mark += int(mark)
        comment.mark -= int(session[f'{current_user.id}']['comments'][str(comment_id)])
        session[f'{current_user.id}'] = {'comments': {f'{comment_id}': mark}}
    elif int(session[f'{current_user.id}']['comments'][str(comment_id)]) + int(mark) <= -1 or int(
            session[f'{current_user.id}']['comments'][str(comment_id)]) + int(mark) >= 1:
        comment.mark -= int(mark)
        session[f'{current_user.id}'] = {'comments': {f'{comment_id}': '0'}}
    db_sess.commit()


def create_comment(text: str, article_id: articles.Articles.id, answer_on: str | None) -> None:
    comment = comments.Comments(user_id=current_user.id, text=text, article_id=article_id,
                                created_date=datetime.datetime.now(), answer_on=answer_on)
    comment.level = get_comment(int(answer_on)).level + 1 if answer_on else 0
    db_sess.add(comment)
    db_sess.commit()


def get_answers(comment_id) -> list:
    return db_sess.query(comments.Comments).filter(comments.Comments.answer_on == comment_id).all()


def get_comment(comment_id):
    return db_sess.query(comments.Comments).filter(comments.Comments.id == comment_id).first()