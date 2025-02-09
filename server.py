import datetime
import os
from flask_login import *
from flask import *
from data import db_session, articles, users, comments
from forms.ArticleForm import *
from werkzeug.utils import secure_filename
from sqlalchemy import desc, and_, or_
import json
from forms.UserForm import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['UPLOAD_FOLDER'] = './static/images'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(users.User).get(user_id)


def getMostPopularArticle(category=None):
    db_sess = db_session.create_session()
    if category is None:
        return db_sess.query(articles.Articles).filter(articles.Articles.created_date.ilike('%'+ f'{datetime.datetime.today().date()}' + '%')).order_by(
        desc(articles.Articles.readings))
    if category == 'subscribed':
        if current_user.is_authenticated and current_user.subscribed:
            all_subs = [int(i) for i, k in json.loads(current_user.subscribed).items() if k == '1']
            return db_sess.query(articles.Articles).filter(and_(
                    articles.Articles.created_date.ilike('%' + str(datetime.datetime.today().date()) + '%'),
                    articles.Articles.user_id.in_(all_subs))).order_by(
                    desc(articles.Articles.readings)).all()
        else:
            return []
    categories = {'top': 'Топ', 'reviews': 'Обзоры', 'comparison': 'Сравнения'}
    return db_sess.query(articles.Articles).filter(and_(
                articles.Articles.created_date.ilike('%' + str(datetime.datetime.today().date()) + '%'),
                articles.Articles.categories == categories[category])).order_by(
                desc(articles.Articles.readings)).all()


@app.route('/all/<category>', methods=['GET', 'POST'])
def all_category(category):
    all_articles = getMostPopularArticle(category)
    db_sess = db_session.create_session()
    creators = {}
    amount_comments_articles = {}
    to_delete = request.form.get('delete')
    if to_delete:
        db_sess.query(articles.Articles).filter(articles.Articles.id == to_delete).delete()
        db_sess.commit()
    for article in all_articles:
        creator = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
        time_delta = datetime.datetime.now() - article.created_date
        time = text_delta(time_delta)
        creators[str(article.id)] = (creator.name, creator.photo, creator.subscribers, time)
        amount_comments_articles[str(article.id)] = len(
            db_sess.query(comments.Comment).filter(comments.Comment.article_id == article.id).all())
    id_article = request.form.get('id')
    if id_article:
        article = db_sess.query(articles.Articles).filter(articles.Articles.id == id_article).first()
        article.readings += 1
        user = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
        user.reading += 1
        db_sess.commit()
        return redirect(f'/article/{id_article}/read')
    return render_template('all_articles.html', link=category, amount_comments_articles=amount_comments_articles, creators=creators, articles=all_articles, current_user=current_user)


@app.route('/search', methods=['GET', 'POST'])
def search():
    to_search = request.form.get('to_search')
    text = request.form.get('search')
    db_sess = db_session.create_session()
    id_article = request.form.get('id')
    all_articles = []
    creators = {}
    amount_comments_articles = {}
    to_delete = request.form.get('delete')
    if to_delete:
        db_sess.query(articles.Articles).filter(articles.Articles.id == to_delete).delete()
        db_sess.commit()
    if to_search:
        all_articles = db_sess.query(articles.Articles).filter(articles.Articles.name.ilike('%' + text + '%')).order_by(desc(articles.Articles.readings)).all()
        for article in all_articles:
            creator = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
            time_delta = datetime.datetime.now() - article.created_date
            time = text_delta(time_delta)
            creators[str(article.id)] = (creator.name, creator.photo, creator.subscribers, time)
            amount_comments_articles[str(article.id)] = len(
                db_sess.query(comments.Comment).filter(comments.Comment.article_id == article.id).all())
    if not text:
        return render_template('all_articles.html', amount_comments_articles=amount_comments_articles,
                               creators=creators, articles=[], current_user=current_user, search=True)
    if id_article:
        article = db_sess.query(articles.Articles).filter(articles.Articles.id == id_article).first()
        article.readings += 1
        user = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
        user.reading += 1
        db_sess.commit()
        return redirect(f'/article/{id_article}/read')
    return render_template('all_articles.html', amount_comments_articles=amount_comments_articles, creators=creators, articles=all_articles, current_user=current_user, search=True)


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



@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    db_sess = db_session.create_session()
    db_sess.query(articles.Articles).filter(articles.Articles.text == None).delete()
    db_sess.commit()
    mark_leaders = db_sess.query(users.User).order_by(desc(users.User.mark))
    reading_leaders = db_sess.query(users.User).order_by(desc(users.User.reading))
    subscribers_leaders = db_sess.query(users.User).order_by(desc(users.User.subscribers))
    top_russia = getMostPopularArticle('tops')
    top_china = getMostPopularArticle('reviews')
    top_foreign = getMostPopularArticle('comparisons')
    amount_comments_articles = {}
    popular_articles = getMostPopularArticle()
    creators = {}
    for article in popular_articles:
        creator = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
        time_delta = datetime.datetime.now() - article.created_date
        time = text_delta(time_delta)
        creators[str(article.id)] = (creator.name, creator.photo, creator.subscribers, time)
        amount_comments_articles[str(article.id)] = len(db_sess.query(comments.Comment).filter(comments.Comment.article_id == article.id).all())
    id_article = request.form.get('id')
    to_delete = request.form.get('delete')
    if to_delete:
        db_sess.query(articles.Articles).filter(articles.Articles.id == to_delete).delete()
        db_sess.commit()
    if id_article:
        article = db_sess.query(articles.Articles).filter(articles.Articles.id == id_article).first()
        article.readings += 1
        user = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
        user.reading += 1
        db_sess.commit()
        return redirect(f'/article/{id_article}/read')
    elif len(db_sess.query(users.User).all()) < 5:
        return render_template('index.html', articles=popular_articles, users=users.User(),creators=creators,top_russia=top_russia, top_china=top_china, top_foreign=top_foreign, mark_leaders=False, amount_comments_articles=amount_comments_articles,
                               readings_leaders=False, subscribers_leaders=False)
    return render_template('index.html', top_russia=top_russia, top_china=top_china, top_foreign=top_foreign, creators=creators, amount_comments_articles=amount_comments_articles, articles=popular_articles, users= db_sess.query(users.User).all(), mark_leaders=mark_leaders, readings_leaders=reading_leaders,  subscribers_leaders=subscribers_leaders)


@app.route('/all/<category>', methods=['GET', 'POST'])
def popular_category_articles(category):
    popular_articles = getMostPopularArticle(category)
    clickedOnArticle()
    return render_template('index.html', articles=popular_articles)


def clickedOnArticle():
    id_article = request.form.get('id')
    if id_article:
        return redirect(f'/article/{id_article}/read')


def getSearchArticles():
    db_sess = db_session.create_session()
    search_articles = request.args.get('search')
    return db_sess.query(articles.Articles).filter(articles.Articles.name.ilike('%' + search_articles + '%')).all()


@app.route('/register', methods=['GET', 'POST'])
def registerUser():
    form = RegisterForm()
    if form.to_login.data:
        return redirect('/login')
    elif form.validate_on_submit():
        if userAlreadyExist(form.username.data):
            return render_template('register.html', form=form, message="Такой пользователь уже есть")
        createUser()
        return redirect('/')
    return render_template('register.html', form=form)


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.register.data:
        return redirect('/register')
    elif form.validate_on_submit():
        checkAndLoginUser(form.username.data, form.password.data)
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form, current_user=current_user)


def checkAndLoginUser(name, password):
    db_sess = db_session.create_session()
    user = db_sess.query(users.User).filter(users.User.name == name).first()
    if user and user.check_password(password):
        login_user(user)
        return redirect("/")


@app.route('/article/<article_id>/read', methods=['GET', 'POST'])
def reading_article(article_id):
    comment_form = CommentsArticle()
    db_sess = db_session.create_session()
    make_comment = request.form.get('comment')
    text = comment_form.text.data
    to_answer = request.form.get('to_answer')
    make_answer = request.form.get('make_answer')
    answer_text = request.form.get('answer_input')
    if make_answer and answer_text != '':
        comment = comments.Comment(user=current_user.id, text=answer_text, article_id=article_id,
                                   created_date=str(datetime.datetime.now()), answer_on=make_answer)
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f'/article/{article_id}/read')
    if make_comment == '1' and text != '':
        comment = comments.Comment(user=current_user.id, text=text, article_id=article_id,
                                   created_date=datetime.datetime.now())
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f'/article/{article_id}/read')
    article = db_sess.query(articles.Articles).filter(articles.Articles.id == article_id).first()
    user = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
    all_comments = db_sess.query(comments.Comment).filter(comments.Comment.article_id == article_id).all()
    answers_comments = {}
    creators_comments = {}
    for comment in all_comments:
        answers_comments[str(comment.id)] = db_sess.query(comments.Comment).filter(comments.Comment.answer_on == comment.id).all()
        creator = db_sess.query(users.User).filter(users.User.id == comment.user).first()
        time_delta = datetime.datetime.now() - comment.created_date
        time = text_delta(time_delta)
        creators_comments[str(comment.id)] = (creator.name, creator.photo, creator.subscribers, time)
    to_subscribe = request.form.get('to_subscribe')
    mark = request.form.get('mark')
    comment_make_mark = request.form.get('comment_mark')
    answer = request.form.get('answer')
    time_delta = datetime.datetime.now() - article.created_date
    time = text_delta(time_delta)
    if comment_make_mark:
        comment_id, comment_mark = comment_make_mark.split(',')
        comment = db_sess.query(comments.Comment).filter(comments.Comment.id == comment_id).first()
        if f'{current_user.id}' not in session or 'comments' not in session[str(current_user.id)] or str(
                comment_id) not in session[f'{current_user.id}']['comments']:
            comment.mark += int(comment_mark)
            db_sess.commit()
            session[f'{current_user.id}'] = {'comments': {f'{comment_id}': comment_mark}}
        elif 1 >= int(session[f'{current_user.id}']['comments'][str(comment_id)]) + int(comment_mark) >= -1:
            comment.mark += int(comment_mark)
            comment.mark -= int(session[f'{current_user.id}']['comments'][str(comment_id)])
            db_sess.commit()
            session[f'{current_user.id}'] = {'comments': {f'{comment_id}': comment_mark}}
        elif int(session[f'{current_user.id}']['comments'][str(comment_id)]) + int(comment_mark) <= -1 or int(
                session[f'{current_user.id}']['comments'][str(comment_id)]) + int(comment_mark) >= 1:
            comment.mark -= int(comment_mark)
            db_sess.commit()
            session[f'{current_user.id}'] = {'comments': {f'{comment_id}': '0'}}
    this_user = db_sess.query(users.User).filter(users.User.id == current_user.id).first()
    if mark:
        if this_user.marked_articles:
            prev_mark = json.loads(this_user.marked_articles)
        else:
            prev_mark = {}
        if (not prev_mark) or (not str(article_id) in prev_mark.keys()):
            article.mark += int(mark)
            user.mark += int(mark)
            prev_mark[str(article_id)] = str(mark)
        elif 1 >= int(prev_mark[str(article_id)]) + int(mark) >= -1:
            article.mark += int(mark)
            article.mark -= int(prev_mark[str(article_id)])
            user.mark += int(mark)
            user.mark -= int(prev_mark[str(article_id)])
            prev_mark[str(article_id)] = str(mark)
        elif int(prev_mark[str(article_id)]) + int(mark) <= -1 or int(prev_mark[str(article_id)]) + int(mark) >= 1:
            article.mark -= int(mark)
            user.mark -= int(mark)
            prev_mark[str(article_id)] = '0'
        this_user.marked_articles = json.dumps(prev_mark)
        db_sess.commit()
    if to_subscribe and article.user_id != current_user.id:
        if this_user.subscribed:
            prev_subs = json.loads(this_user.subscribed)
        else:
            prev_subs = {}
        if (not prev_subs) or (str(user.id) not in prev_subs) or (prev_subs[str(user.id)] == '0'):
            user.subscribers += 1
            prev_subs[str(user.id)] = '1'
        elif prev_subs[str(user.id)] == '1':
            user.subscribers -= 1
            prev_subs[str(user.id)] = '0'
        this_user.subscribed = json.dumps(prev_subs)
        db_sess.commit()
    if this_user.subscribed:
        all_subs = [i for i, k in json.loads(this_user.subscribed).items() if k == '1']
        if str(user.id) in all_subs:
            is_subscribed = 1
        else:
            is_subscribed = 0
    else:
        is_subscribed = 0
    return render_template('reading_article.html', time=time, is_subscribed=is_subscribed, creators_comments=creators_comments,
                           answers_comments=answers_comments, to_answer=to_answer, comment_form=comment_form,
                           amount_comments=len(all_comments), answer=answer, time_now=datetime.datetime.now(),
                           article=article, current_user=current_user, user=user, all_comments=all_comments)


def getCreatorArticle(article):
    db_sess = db_session.create_session()
    return db_sess.query(users.User).filter(users.User.id == article.user_id).first()


def deleteArticle(article):
    db_sess = db_session.create_session()
    db_sess.query(articles.Articles).filter(articles.Articles.id == article.id).delete()
    db_sess.commit()


@app.route('/create_article', methods=['GET', 'POST'])
def create_article():
    form = CreatingArticleDataForm()
    data = request.form.get('input')
    if form.create.data and data != '' and form.validate_on_submit():
        data = data.replace('<img', '<img height="100%" width="100%"')
        addArticle(data, form)
        return redirect('/')
    return render_template('write_article.html', current_user=current_user, form=form)


def addArticle(text, form):
    article = articles.Articles()
    article.text = text
    article.user_id = current_user.id
    article.created_date = datetime.datetime.now()
    db_sess = db_session.create_session()
    file = form.photo.data
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        article.photo = filename
    article.name = form.name.data
    article.describe = form.describe.data
    article.categories = form.category.data
    db_sess.add(article)
    db_sess.commit()



@app.route('/change_article/<article_id>', methods=['GET', 'POST'])
def change_article(article_id):
    form = ChangingArticleForm()
    article = getArticle(article_id)
    if form.validate_on_submit():
        refactorArticle(article, form)
    return render_template('create_article.html', title='Изменение статьи', form=form, current_user=current_user)


def refactorArticle(article, form):
    db_sess = db_session.create_session()
    article.name = form.name.data
    article.category = form.category.data
    article.describe = form.describe.data
    article.created_date = datetime.date.today()
    db_sess.commit()


def getUser(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(users.User).filter(users.User.id == user_id).first()
    return user


@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile_user(user_id):
    form = ProfileView()
    db_sess = db_session.create_session()
    user = db_sess.query(users.User).filter(users.User.id == user_id).first()
    created_articles = db_sess.query(articles.Articles).filter(articles.Articles.user_id == user.id).all()
    add_data = form.add_data.data
    contacts = user.contacts
    description = user.description
    amount_articles = len(created_articles)
    mark = 0
    to_subscribe = request.form.get('to_subscribe')
    if user.subscribed:
        all_id_subscriptions = [i for i, k in json.loads(user.subscribed).items() if k == '1']
        all_subscriptions = []
        for i in all_id_subscriptions:
            all_subscriptions.append(db_sess.query(users.User).filter(users.User.id == int(i)).first())
    this_user = db_sess.query(users.User).filter(users.User.id == current_user.id).first()
    if to_subscribe:
        if this_user.subscribed:
            prev_subs = json.loads(this_user.subscribed)
        else:
            prev_subs = {}
        if (not prev_subs) or (prev_subs[str(user_id)] == '0'):
            user.subscribers += 1
            prev_subs[str(user_id)] = '1'
        elif prev_subs[str(user_id)] == '1':
            user.subscribers -= 1
            prev_subs[str(user_id)] = '0'
        this_user.subscribed = json.dumps(prev_subs)
        db_sess.commit()
    subscribers = user.subscribers
    all_users = []
    add_articles = []
    if form.subscribe.data and user.subscribed:
        all_subs = [i for i, k in json.loads(user.subscribed).items() if k == '1']
        for sub in all_subs:
            all_users.append(db_sess.query(users.User).filter(users.User.id == int(sub)).first())
    if form.follow.data and user.marked_articles:
        all_followed = [i for i, k in json.loads(user.marked_articles).items() if k == '1']
        for art in all_followed:
            add_articles.append(db_sess.query(articles.Articles).filter(articles.Articles.id==int(art)).first())
        amount_comments_articles = {}
        for article in add_articles:
            amount_comments_articles[str(article.id)] = len(
                db_sess.query(comments.Comment).filter(comments.Comment.article_id == article.id).all())
        if not add_articles:
            return 'Пользователь не создал ни одной статьи'
    if add_data:
        return redirect(f'/profile_data/{user_id}')
    id_article = request.form.get('id')
    if id_article:
        article = db_sess.query(articles.Articles).filter(articles.Articles.id == id_article).first()
        article.readings += 1
        user = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
        user.reading += 1
        db_sess.commit()
        return redirect(f'/article/{id_article}/read')
    for article in created_articles:
        mark += article.mark
    if form.created_articles.data:
        add_articles = db_sess.query(articles.Articles).filter(articles.Articles.user_id == user_id).all()
        if not add_articles:
            return 'Пользователь не создал ни одной статьи'
    creators = {}
    amount_comments_articles = {}
    to_delete = request.form.get('delete')
    if to_delete:
        db_sess.query(articles.Articles).filter(articles.Articles.id == to_delete).delete()
        db_sess.commit()
    for article in add_articles:
        creator = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
        time_delta = datetime.datetime.now() - article.created_date
        time = text_delta(time_delta)
        creators[str(article.id)] = (creator.name, creator.photo, creator.subscribers, time)
        amount_comments_articles[str(article.id)] = len(
            db_sess.query(comments.Comment).filter(comments.Comment.article_id == article.id).all())
    if form.exit.data:
        logout_user()
        return redirect('/')
    if this_user.subscribed:
        all_subs = [i for i, k in json.loads(this_user.subscribed).items() if k == '1']
        if str(user_id) in all_subs:
            is_subscribed = 1
        else:
            is_subscribed = 0
    else:
        is_subscribed = 0
    return render_template('profile_check.html', add_articles=add_articles, creators=creators, amount_comments_articles=amount_comments_articles, is_subscribed=is_subscribed, contacts=contacts, description=description, photo=user.photo, amount_articles=amount_articles, subscribers=subscribers,
                           mark=mark, name=user.name, form=form, current_user=current_user, user_id=int(user_id), all_users=all_users)

@app.route('/profile_data/<user_id>', methods=['GET', 'POST'])
def descript_user(user_id):
    form = DescriptionProfile()
    db_sess = db_session.create_session()
    if form.create.data:
        user = db_sess.query(users.User).filter(users.User.id == user_id).first()
        user.name = form.name.data
        photo = form.photo.data
        if photo:
           filename = secure_filename(photo.filename)
           photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
           user.photo = filename
        user.description = form.description.data
        user.contacts = form.contacts.data
        db_sess.commit()
        return redirect(f'/profile/{user_id}')
    return render_template('profile_data.html', form=form)


@app.route('/created_articles/<user_id>', methods=['GET', 'POST'])
def show_user_articles(user_id):
    db_sess = db_session.create_session()
    user_articles = db_sess.query(articles.Articles).filter(articles.Articles.user_id == user_id).all()
    if request.method == 'POST':
        article_id = request.form.get('id')
        return redirect(f'/articles/{article_id}/reading')
    if not user_articles:
        return 'Пользователь не создал ни одной статьи'
    return render_template('all_articles.html', articles=user_articles, current_user=current_user,
                           title=f'Статьи пользователя{current_user.name}')


def getUserArticles(user_id):
    db_sess = db_session.create_session()
    user_articles = db_sess.query(articles.Articles).filter(articles.Articles.user_id == user_id).all()
    return user_articles


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
