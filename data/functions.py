from data import users, articles, db_session, comments, questions, answers
from sqlalchemy import desc, and_
from flask import *
from email_validator import validate_email
from typing import NamedTuple, Type
import json
import datetime
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
import os
from forms.ArticleForm import *
from forms.UserForm import *
from flask_login import *
from data.users import Users
from mailing import send_simple_email
from random import randint
from forms.ForumForm import *

db_session.global_init("db/blogs.sql")
db_sess = db_session.create_session()


class TopArticle(NamedTuple):
    tops: Type[articles.Articles]
    reviews: Type[articles.Articles]
    comparisons: Type[articles.Articles]
    news: Type[articles.Articles]


def create_article(text: str, form: CreatingArticleDataForm, user_id: Users.id, app, brand, photo) -> None:
    text = text.replace('<img', '<img height="100%" width="100%"')
    article = articles.Articles(text=text, user_id=user_id, created_date=datetime.datetime.now(),
                                brand=brand, body=form.body_category.data,
                                name=form.name.data, describe=form.describe.data, categories=form.category.data)
    add_photo(photo, article, app)
    db_sess.add(article)
    db_sess.commit()


def change_article(text: str, form: EditArticleForm, article_id: int, app, brand, photo) -> None:
    text = text.replace('<img', '<img height="100%" width="100%"')
    article = get_article(article_id)
    article.text = text
    article.brand = brand
    article.body = form.body_category.data
    article.name = form.name.data
    article.describe = form.describe.data
    article.categories = form.category.data
    add_photo(photo, article, app)
    db_sess.commit()


def check_article_data(data: CreatingArticleDataForm, text):
    if len(data.name.data) < 5:
        return 'Имя слишком короткое! Минимальная длина - 5 символов'
    elif len(data.name.data) > 30:
        return 'Имя слишком длинное! Максимальная длина - 30 символов'
    if len(BeautifulSoup(text).get_text()) < 50:
        return 'Текст слишком короткий! Минимальная длина - 50 символов'
    if len(BeautifulSoup(text).get_text()) > 10000:
        return 'Текст слишком короткий! Максимальная длина - 10000 символов'
    if len(data.describe.data) > 200:
        return 'Описание слишком длинное! Максимальная длина - 100 символов'
    if data.category.data == '':
        return 'Тип статьи обязателен для заполнения!'
    return False


def add_photo(file, article, app) -> None:
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        article.photo = filename


def get_on_category(category: str = None) -> list[Type[articles.Articles]]:
    if category is None:
        return db_sess.query(articles.Articles).filter(articles.Articles.categories != 'Новости').all()[::-1][:20]
    elif category == 'subscribed' and current_user.is_authenticated:
        return get_article_subscribed(current_user)
    elif category != 'subscribed':
        categories = {'tops': 'Топ', 'reviews': 'Обзоры', 'comparisons': 'Сравнения', 'news': 'Новости'}
        body_categories = {'sedans': ['Седан', 'Универсал'], 'trucks': ['Хэтчбек', 'Внедорожник'], 'electro': ['Электро']}
        countries = {
            'russia': ['Lada', 'УАЗ'],
            'foreign': ['Volkswagen', 'Ford', 'Chevrolet', 'BMW', 'Mercedes-Benz', 'Audi', 'Land Rover', 'Porshe', 'Renault', 'Skoda', 'Volvo', 'Opel'],
            'asia': ['Toyota', 'Honda', 'Nissan', 'Hyundai', 'Kia', 'Lexus', 'LiXiang', 'Mitsubishi', 'Subaru', 'Exeed', 'Mazda', 'Changan', 'Chery', 'Citroen', 'GAC', 'Geely', 'Haval', 'Hyndai']
        }
        if category in categories:
            return db_sess.query(articles.Articles).filter(articles.Articles.categories == categories[category]).all()[
               ::-1][:20]
        elif category in body_categories.keys():
            return db_sess.query(articles.Articles).filter(and_(articles.Articles.body.in_(body_categories[category]), articles.Articles.categories != 'Новости')).all()[
               ::-1][:20]
        return db_sess.query(articles.Articles).filter(and_(articles.Articles.brand.in_(countries[category]), articles.Articles.categories != 'Новости')).all()[
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


def get_all_news():
    return db_sess.query(articles.Articles).filter(articles.Articles.categories == 'Новости').all()[:4]


def get_article_subscribed(user: Users) -> list[Type[articles.Articles]]:
    all_subs = [int(i) for i, k in json.loads(user.subscribed).items() if k == '1']
    return db_sess.query(articles.Articles).filter(and_(articles.Articles.user_id.in_(all_subs), articles.Articles.categories != 'Новости')).all()


def get_article_from_user(user_id: Users.id) -> list[Type[articles.Articles]]:
    return db_sess.query(articles.Articles).filter(articles.Articles.user_id == user_id).all()


def get_article_data(all_articles: list[Type[articles.Articles]]) -> dict:
    """
        DATA[0] = username
        DATA[1] = user_logo
        DATA[2] = user_subscribers
        DATA[3] = time
        DATA[4] = amount_comments
        DATA[5] = short_mark
        DATA[6] = short_readings
        DATA[7] = short_amount_comments
    """
    data = {}
    for article in all_articles:
        creator = get_user(article.user_id)
        time = text_delta(datetime.datetime.now() - article.created_date)
        data[str(article.id)] = (creator.name, creator.photo, creator.subscribers, time, len(get_comments(article.id)),
                                 short_form(article.mark), short_form(article.readings), short_form(len(get_comments(article.id))))
    return data


def short_form(form: int):
    if 1_000_000 > int(form) >= 1000:
        return f'{form // 1000}k'
    elif form >= 1_000_000:
        return f'{form // 1000000}kk'
    return form


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


def mark_article(article_id: articles.Articles.id, mark: int) -> str:
    article = get_article(article_id)
    user = get_user(current_user.id)
    author = get_user(article.user_id)
    prev_mark = json.loads(user.marked_articles)
    if not mark and prev_mark and str(article_id) in prev_mark.keys(): return prev_mark[str(article_id)]
    elif (not prev_mark) or (not str(article_id) in prev_mark.keys()):
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
    return prev_mark[str(article_id)]


def get_followed(user_id: Users.id) -> list:
    user = get_user(user_id)
    return [get_article(int(i)) for i, k in json.loads(user.marked_articles).items() if k == '1']


def sort_articles_by_time_and_type(time: str, type_sorted: str):
    time_dict = {
        'h': datetime.datetime.now() - datetime.timedelta(hours=1),
        'd': datetime.datetime.now() - datetime.timedelta(days=1),
        'm': datetime.datetime.now() - datetime.timedelta(days=30),
        'y': datetime.datetime.now() - datetime.timedelta(days=365),
        'o': datetime.datetime.now() - datetime.timedelta(days=365*2000)
    }
    type_dict = {
        'm': articles.Articles.mark,
        'r': articles.Articles.readings,
        'p': articles.Articles.id
    }
    return db_sess.query(articles.Articles).order_by(desc(type_dict[type_sorted])).filter(articles.Articles.created_date > time_dict[time]).all()


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


def _is_email_already_exist(email: str) -> bool:
    return bool(len(db_sess.query(Users).filter(Users.email == email).all()))


def check_data_and_send_email(data: LoginForm):
    if not _is_email_already_exist(data.email.data):
        return f'Почта {data.email.data} не зарегестрирована в системе'
    elif not check(data.email.data, data.password.data):
        return f'Пароль {data.password.data} неверный'
    password = send_password(data.email.data, None)
    session[data.email.data] = (data.data, password)
    return False


def check_data_and_register_user(data: RegisterForm):
    try:
        validate_email(data.email.data)
    except Exception:
        return f'Почты {data.email.data} не существует'
    if _is_username_exist(data.username.data):
        return f'Имя {data.username.data} уже используется'
    elif len(data.username.data) < 3:
        return f'Имя {data.username.data} слишком короткое! Минимальная длина - 3 символа'
    elif len(data.username.data) > 20:
        return f'Имя {data.username.data} слишком длинное! Максимальная длина - 20 символов'
    elif _is_email_already_exist(data.email.data):
        return f'Почта {data.email.data} уже используется'
    elif _is_password_already_exist(users.generate_password_hash(data.password.data)):
        return f'Пароль {data.password.data} уже используется'
    elif _is_password_too(data.password.data) == 'short':
        return f'Пароль {data.password.data} слишком простой! Минимальная длина пароля - 8 символов'
    elif _is_password_too(data.password.data) == 'long':
        return f'Пароль {data.password.data} слишком длинный! Максимальная длина пароля - 30 символов'
    elif _is_password_too(data.password.data):
        return f'Пароль {data.password.data} слишком простой! Используйте заглавные буквы и цифры'
    password = send_password(data.email.data, data.username.data)
    session[data.email.data] = (data.data, password)
    return False


def _is_password_already_exist(hashed_password):
    return bool(len(db_sess.query(Users).filter(Users.hashed_password == hashed_password).all()))


def _is_password_too(password: str):
    if len(password) < 8:
        return 'short'
    elif len(password) > 30:
        return 'long'
    elif (not any(i.isalpha() for i in password)) or (not any(i.isupper() for i in password)):
        return 'simple'
    return False


def _is_username_exist(username: str) -> bool:
    return bool(len(db_sess.query(Users).filter(Users.name == username).all()))


def check(email: str, password: str) -> bool:
    user = get_on_email(email)
    return user and user.check_password(password)


def send_password(email, name):
    password = randint(100000, 999999)
    if name is None:
        name = get_on_email(email).name
    send_simple_email(receiver_email=email, body=str(password), username=name)
    return password


def check_email_and_login_user(prev_link, password, email):
    parse_password = session[email][1]
    if str(password) == str(parse_password):
        if prev_link == 'reg':
            create_user(session[email][0])
        else:
            user_log = get_on_email(email)
            login_user(user_log)
        return 'True'
    return 'Неправильный пароль'


def get_on_email(email: str) -> users.Users:
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
    last_id_comment = len(db_sess.query(comments.Comments).order_by(desc(comments.Comments.mark)).filter(
        comments.Comments.article_id == article_id).all())
    id_comment = 1
    while id_comment <= last_id_comment != 0:
        current_comment = get_comment(id_comment)
        answers_on_current_comment = get_answers(id_comment)
        if current_comment in all_sorted_comments and len(answers_on_current_comment) != 0:
            idx_in_asc = all_sorted_comments.index(current_comment)
            all_sorted_comments = [*all_sorted_comments[:idx_in_asc], current_comment, *answers_on_current_comment,
                                   *all_sorted_comments[idx_in_asc + 1:]]
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


def create_question(text: str, form: CreatingQuestionForm, user_id: int, brand: str) -> None:
    text = text.replace('<img', '<img height="100%" width="100%"')
    question = questions.Questions(text=text, user_id=user_id, brand=brand, body=form.body_category.data,name=form.name.data)
    db_sess.add(question)
    db_sess.commit()


def change_question(text: str, form: EditQuestionForm, question_id: int, brand) -> None:
    text = text.replace('<img', '<img height="100%" width="100%"')
    question = get_question(question_id)
    question.text = text
    question.brand = brand
    question.body = form.body_category.data
    question.name = form.name.data
    db_sess.commit()


def check_question_data(data: EditQuestionForm, text):
    if len(data.name.data) < 5:
        return 'Имя слишком короткое! Минимальная длина - 5 символов'
    elif len(data.name.data) > 30:
        return 'Имя слишком длинное! Максимальная длина - 30 символов'
    if len(BeautifulSoup(text).get_text()) < 20:
        return 'Текст слишком короткий! Минимальная длина - 20 символов'
    if len(BeautifulSoup(text).get_text()) > 10000:
        return 'Текст слишком короткий! Максимальная длина - 10000 символов'
    return False


def get_popular_questions() -> list:
    return db_sess.query(questions.Questions).order_by(desc(questions.Questions.created_date)).all()[:20]


def get_questions_from_user(user_id: int) -> list:
    return db_sess.query(questions.Questions).filter(questions.Questions.user_id == user_id).all()


def get_question_data(all_questions) -> dict:
    """
        DATA[0] = username
        DATA[1] = user_logo
        DATA[2] = user_subscribers
        DATA[3] = time
        DATA[4] = amount_answers
        DATA[5] = is_solved
        DATA[6] = short_mark
        DATA[7] = short_readings
        DATA[8] = short_amount_comments
    """
    data = {}
    for question in all_questions:
        creator = get_user(question.user_id)
        time = text_delta(datetime.datetime.now() - question.created_date)
        amount_answers = get_answers_on_question(question.id)
        data[str(question.id)] = (creator.name, creator.photo, creator.subscribers, time, len(amount_answers),
                                 short_form(question.mark), short_form(question.readings), short_form(len(amount_answers)))
    return data


def delete_question(question_id) -> None:
    db_sess.query(questions.Questions).filter(questions.Questions.id == question_id).delete()
    db_sess.commit()


def add_reading_question(question_id: articles.Articles.id) -> None:
    question = get_question(question_id)
    question.readings += 1
    db_sess.commit()


def get_question(question_id: int):
    return db_sess.query(questions.Questions).filter(questions.Questions.id == question_id).first()


def mark_question(question_id: int, mark: int) -> str:
    question = get_question(question_id)
    user = get_user(current_user.id)
    author = get_user(question.user_id)
    prev_mark = json.loads(user.marked_questions)
    if not mark and prev_mark and str(question_id) in prev_mark.keys(): return prev_mark[str(question_id)]
    elif (not prev_mark) or (not str(question_id) in prev_mark.keys()):
        question.mark += mark
        author.mark += mark
        prev_mark[str(question_id)] = str(mark)
    elif 1 >= int(prev_mark[str(question_id)]) + mark >= -1:
        question.mark += (mark - int(prev_mark[str(question_id)]))
        author.mark += (mark - int(prev_mark[str(question_id)]))
        prev_mark[str(question_id)] = str(mark)
    elif not 1 >= int(prev_mark[str(question_id)]) + mark >= -1:
        question.mark -= mark
        author.mark -= mark
        prev_mark[str(question_id)] = '0'
    user.marked_questions = json.dumps(prev_mark)
    db_sess.commit()
    return prev_mark[str(question_id)]


def sort_questions_by_time_and_type(time: str, type_sorted: str):
    time_dict = {
        'h': datetime.datetime.now() - datetime.timedelta(hours=1),
        'd': datetime.datetime.now() - datetime.timedelta(days=1),
        'm': datetime.datetime.now() - datetime.timedelta(days=30),
        'y': datetime.datetime.now() - datetime.timedelta(days=365),
        'o': datetime.datetime.now() - datetime.timedelta(days=365*2000)
    }
    type_dict = {
        'm': questions.Questions.mark,
        'r': questions.Questions.readings,
        'p': questions.Questions.id
    }
    if type_sorted == 's':
        return db_sess.query(questions.Questions).filter(and_(
            articles.Articles.created_date > time_dict[time], questions.Questions.is_solved == True)).all()
    return db_sess.query(articles.Articles).order_by(desc(type_dict[type_sorted])).filter(articles.Articles.created_date > time_dict[time]).all()


def get_experts() -> list | None:
    experts = db_sess.query(Users).order_by(desc(Users.right_answers)).all()[:5]
    if len(experts) > 4:
        return experts


def get_answers_on_question(question_id: int):
    popular_right = db_sess.query(answers.Answers).filter(and_(answers.Answers.is_right == True, answers.Answers.question_id == question_id)).all()
    popular_not_right = db_sess.query(answers.Answers).filter(and_(answers.Answers.is_right != 1, answers.Answers.question_id == question_id)).all()
    return [*popular_right, *popular_not_right]


def create_answer(text, question_id):
    answer = answers.Answers(user_id=current_user.id, text=text, question_id=question_id)
    db_sess.add(answer)
    db_sess.commit()


def get_answers_data(all_answers):
    data = {}
    for answer in all_answers:
        creator = get_user(answer.user_id)
        time = text_delta(datetime.datetime.now() - answer.created_date)
        data[str(answer.id)] = (creator.name, creator.photo, creator.subscribers, time)
    return data


def mark_answer(answer_id, mark):
    answer = db_sess.query(answers.Answers).filter(answers.Answers.id == answer_id).first()
    if f'{current_user.id}' not in session or 'answers' not in session[str(current_user.id)] or str(
            answer_id) not in session[f'{current_user.id}']['answers']:
        answer.mark += mark
        session[f'{current_user.id}'] = {'answers': {f'{answer_id}': mark}}
    elif 1 >= int(session[f'{current_user.id}']['answers'][str(answer_id)]) + int(mark) >= -1:
        answer.mark += int(mark)
        answer.mark -= int(session[f'{current_user.id}']['answers'][str(answer_id)])
        session[f'{current_user.id}'] = {'answers': {f'{answer_id}': mark}}
    elif int(session[f'{current_user.id}']['answers'][str(answer_id)]) + int(mark) <= -1 or int(
            session[f'{current_user.id}']['answers'][str(answer_id)]) + int(mark) >= 1:
        answer.mark -= int(mark)
        session[f'{current_user.id}'] = {'answers': {f'{answer_id}': '0'}}
    db_sess.commit()


def make_right_answer(answer_id: int):
    answer = db_sess.query(answers.Answers).filter(answers.Answers.id == answer_id).first()
    answer.is_right = True
    user = get_user(answer.user_id)
    user.right_answers += 1
    question = get_question(answer.question_id)
    question.is_solved = True
    db_sess.commit()


def make_false_answer(answer_id: int):
    answer = db_sess.query(answers.Answers).filter(answers.Answers.id == answer_id).first()
    answer.is_right = False
    user = get_user(answer.user_id)
    user.right_answers -= 1
    db_sess.commit()
    question = get_question(answer.question_id)
    question_right_answers = db_sess.query(answers.Answers).filter(and_(answers.Answers.is_right == True, answers.Answers.question_id == question.id)).all()
    if not question_right_answers:
        question.is_solved = False
        db_sess.commit()



def sort_questions_by_time_and_type(time: str, type_sorted: str):
    time_dict = {
        'h': datetime.datetime.now() - datetime.timedelta(hours=1),
        'd': datetime.datetime.now() - datetime.timedelta(days=1),
        'm': datetime.datetime.now() - datetime.timedelta(days=30),
        'y': datetime.datetime.now() - datetime.timedelta(days=365),
        'o': datetime.datetime.now() - datetime.timedelta(days=365*2000)
    }
    type_dict = {
        'm': questions.Questions.mark,
        'r': questions.Questions.readings,
        'p': questions.Questions.id
    }
    if type_sorted == 's':
        return db_sess.query(questions.Questions).filter(
            and_(questions.Questions.created_date > time_dict[time], questions.Questions.is_solved == True)).all()
    return db_sess.query(questions.Questions).order_by(desc(type_dict[type_sorted])).filter(questions.Questions.created_date > time_dict[time]).all()
