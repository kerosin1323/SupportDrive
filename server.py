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
app.config['UPLOAD_FOLDER'] = '.\static\images'
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
    categories = {'news': 'Новости', 'sedans': 'Легковые', 'trucks': 'Грузовые', 'electrics': 'Электро', 'china': 'Китайские', 'russia': 'Российские', 'foreign': 'Иномарки'}
    return db_sess.query(articles.Articles).filter(and_(
                articles.Articles.created_date.ilike('%' + str(datetime.datetime.today().date()) + '%'),
                articles.Articles.categories == categories[category])).order_by(
                desc(articles.Articles.readings)).all()


@app.route('/all/<category>', methods=['GET', 'POST'])
def all_category(category):
    all_articles = getMostPopularArticle(category)
    id_article = request.form.get('id')
    db_sess = db_session.create_session()
    if id_article:
        article = db_sess.query(articles.Articles).filter(articles.Articles.id == id_article).first()
        article.readings += 1
        db_sess.commit()
        return redirect(f'/article/{id_article}/read')
    return render_template('all_articles.html', articles=all_articles, current_user=current_user)


@app.route('/search', methods=['GET', 'POST'])
def search():
    to_search = request.form.get('to_search')
    text = request.form.get('search')
    db_sess = db_session.create_session()
    id_article = request.form.get('id')
    article = []
    if to_search:
        article = db_sess.query(articles.Articles).filter(or_(
            articles.Articles.name.ilike('%' + text + '%'), articles.Articles.key_words.ilike('%' + text + '%'))).order_by(
            desc(articles.Articles.readings))
    if id_article:
        article = db_sess.query(articles.Articles).filter(articles.Articles.id == id_article).first()
        article.readings += 1
        db_sess.commit()
        return redirect(f'/article/{id_article}/read')
    return render_template('all_articles.html', articles=article, current_user=current_user, search=True)


@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    db_sess = db_session.create_session()
    db_sess.query(articles.Articles).filter(articles.Articles.text == None).delete()
    db_sess.commit()
    mark_leaders = db_sess.query(users.User).order_by(desc(users.User.mark))
    top_articles_sedans = getMostPopularArticle('sedans')
    top_articles_trucks = getMostPopularArticle('trucks')
    top_articles_russia = getMostPopularArticle('russia')
    top_articles_china = getMostPopularArticle('china')
    top_articles_foreign = getMostPopularArticle('foreign')
    top_articles_electrics = getMostPopularArticle('electrics')
    reading_leaders = db_sess.query(users.User).order_by(desc(users.User.reading))
    subscribers_leaders = db_sess.query(users.User).order_by(desc(users.User.subscribers))
    popular_articles = getMostPopularArticle()
    id_article = request.form.get('id')
    to_delete = request.form.get('delete')
    if to_delete:
        db_sess.query(articles.Articles).filter(articles.Articles.id == to_delete).delete()
        db_sess.commit()
    if id_article:
        article = db_sess.query(articles.Articles).filter(articles.Articles.id == id_article).first()
        article.readings += 1
        db_sess.commit()
        return redirect(f'/article/{id_article}/read')
    elif len(db_sess.query(users.User).all()) < 5:
        return render_template('index.html', articles=popular_articles, users=users.User(), mark_leaders=False,
                               readings_leaders=False, subscribers_leaders=False, top_sedan=top_articles_sedans, top_truck=top_articles_trucks, top_foreign=top_articles_foreign, top_china=top_articles_china, top_russia=top_articles_russia, top_elecric=top_articles_electrics)
    return render_template('index.html', articles=popular_articles, users= db_sess.query(users.User).all(), mark_leaders=mark_leaders, readings_leaders=reading_leaders,  subscribers_leaders=subscribers_leaders)


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
    db_sess = db_session.create_session()
    make_comment = request.form.get('comment')
    text = request.form.get('input')
    if make_comment == '1' and text != '':
        creator = db_sess.query(users.User).filter(users.User.id == current_user.id).first()
        comment = comments.Comment(username=creator.name, user=current_user.id, text=text, article_id=article_id,
                                   created_date=str(datetime.datetime.now()))
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f'/article/{article_id}/read')
    article = db_sess.query(articles.Articles).filter(articles.Articles.id == article_id).first()
    user = db_sess.query(users.User).filter(users.User.id == article.user_id).first()
    all_comments = db_sess.query(comments.Comment).filter(comments.Comment.article_id == article_id).all()
    to_subscribe = request.form.get('to_subscribe')
    mark = request.form.get('mark')
    comment_make_mark = request.form.get('comment_mark')
    answer = request.form.get('answer')
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
    if mark:
        if f'{current_user.id}' not in session or 'articles' not in session[str(current_user.id)] or str(article_id) not in session[f'{current_user.id}']['articles']:
            article.mark += int(mark)
            db_sess.commit()
            session[f'{current_user.id}'] = {'articles': {f'{article_id}': mark}}
        elif 1 >= int(session[f'{current_user.id}']['articles'][str(article_id)]) + int(mark) >= -1:
            article.mark += int(mark)
            article.mark -= int(session[f'{current_user.id}']['articles'][str(article_id)])
            db_sess.commit()
            session[f'{current_user.id}'] = {'articles': {f'{article_id}': mark}}
        elif int(session[f'{current_user.id}']['articles'][str(article_id)]) + int(mark) <= -1 or int(session[f'{current_user.id}']['articles'][str(article_id)]) + int(mark) >= 1:
            article.mark -= int(mark)
            db_sess.commit()
            session[f'{current_user.id}'] = {'articles': {f'{article_id}': '0'}}
    if to_subscribe:
        user.subscribers += 1
        db_sess.commit()
    return render_template('reading_article.html', answer=answer, time_now = datetime.datetime.now(), article=article, current_user=current_user, user=user, all_comments=all_comments)


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
    elif data == '':
        return 'Текст не должен быть пустым'
    return render_template('write_article.html', current_user=current_user, form=form)


def addArticle(text, form):
    article = articles.Articles()
    article.text = text
    article.user_id = current_user.id
    article.created_date = str(datetime.datetime.now())
    db_sess = db_session.create_session()
    file = form.photo.data
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        article.photo = filename
    article.name = form.name.data
    article.describe = form.describe.data
    article.categories = form.category.data
    article.key_words = form.key_words.data
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
    subscribers = user.subscribers
    amount_articles = len(created_articles)
    mark = 0
    to_subscribe = request.form.get('to_subscribe')
    photo = form.photo.data
    if photo:
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user.photo = filename
        db_sess.commit()
    if to_subscribe:
        user = db_sess.query(users.User).filter(users.User.id == user_id).first()
        user.subscribers += 1
        db_sess.commit()
    for article in created_articles:
        mark += article.mark
    if form.created_articles.data:
        return redirect(f'/created_articles/{user.id}')
    if form.exit.data:
        logout_user()
        return redirect('/')
    return render_template('profile_check.html', photo=user.photo, amount_articles=amount_articles, subscribers=subscribers,
                           mark=mark, name=user.name, form=form, current_user=current_user, user_id=int(user_id))


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
