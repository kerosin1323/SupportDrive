import datetime
import os
from flask_login import *
from flask import *
from data import db_session, articles, users
from forms.ArticleForm import *
from werkzeug.utils import secure_filename
from sqlalchemy import desc, and_
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


def deleteNoneArticles():
    db_sess = db_session.create_session()
    db_sess.query(articles.Articles).filter(articles.Articles.text is None).delete()
    db_sess.commit()


def getMostPopularArticle(category=None):
    db_sess = db_session.create_session()
    if category is None:
        return db_sess.query(articles.Articles).order_by(desc(articles.Articles.mark))
    return db_sess.query(articles.Articles).filter(articles.Articles.categories.ilike('%' + category + '%')).order_by(
        desc(articles.Articles.mark))


@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    deleteNoneArticles()
    popular_articles = getMostPopularArticle()
    clickedOnArticle()
    return render_template('index.html', articles=popular_articles)


@app.route('/all/<category>', methods=['GET', 'POST'])
def popular_category_articles(category):
    popular_articles = getMostPopularArticle(category)
    clickedOnArticle()
    return render_template('index.html', articles=popular_articles)


def clickedOnArticle():
    id_article = request.form.get('id')
    if id_article:
        return redirect(f'/article/{id_article}/start')


def getSearchArticles():
    db_sess = db_session.create_session()
    search_articles = request.args.get('search')
    return db_sess.query(articles.Articles).filter(articles.Articles.name.ilike('%' + search_articles + '%')).all()


@app.route('/search', methods=['GET', 'POST'])
def search():
    search_articles = getSearchArticles()
    if not search_articles:
        return 'Тестов с таким названием нет'
    if request.method == 'POST' and search_articles:
        clickedOnArticle()
    return render_template('all_search_articles.html', articles=search_articles, current_user=current_user,
                           title=f'Тесты по названию {search_articles[0].name}')


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


@app.route('/articles/<article_id>/start', methods=['GET', 'POST'])
def reading_article(article_id):
    article = getArticle(article_id)
    user = getCreatorArticle(article)

    user_pressed = request.form.get('user')
    to_delete = request.form.get('delete')
    to_change = request.form.get('change')

    if user_pressed:
        return redirect(f'/profile/{user.id}')
    elif to_delete:
        deleteArticle(article)
        return redirect('/')
    elif to_change:
        return redirect(f'/change_article/{article_id}')
    return render_template('reading_article.html', article=article, mark=article.mark, current_user=current_user,
                           user=user)


def getArticle(article_id):
    db_sess = db_session.create_session()
    return db_sess.query(articles.Articles).filter(articles.Articles.id == article_id).first()


def getCreatorArticle(article):
    db_sess = db_session.create_session()
    return db_sess.query(users.User).filter(users.User.id == article.user_id).first()


def deleteArticle(article):
    db_sess = db_session.create_session()
    db_sess.query(articles.Articles).filter(articles.Articles.id == article.id).delete()
    db_sess.commit()


@app.route('/create_article', methods=['GET', 'POST'])
def write_article():
    form = CreatingArticleForm()
    menu = ArticleMenu()
    redactor = TextRedactor()
    if form.validate_on_submit():
        create_article(form)
        return redirect('/create_article/data')
    return render_template('write_article.html', form=form, current_user=current_user)


def create_article(articleData):
    article = articles.Articles()
    article.name = articleData.name.data
    article.text = articleData.text.data
    article.user_id = current_user.id
    article.created_date = datetime.date.today()
    db_sess = db_session.create_session()
    db_sess.add(article)
    db_sess.commit()


@app.route('/create_article/data', methods=['GET', 'POST'])
def create_article_data():
    form = CreatingArticleDataForm()
    if form.validate_on_submit():
        addDataArticle(form)
    return render_template('add_data_article.html', form=form)


def addDataArticle(data):
    article = articles.Articles()
    file = data.photo.data
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    article.photo = filename
    article.category = data.category.data
    article.key_words = data.key_words.data
    db_sess = db_session.create_session()
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


@app.route('/profile', methods=['GET', 'POST'])
def user_profile():
    form = ProfileView()
    user = getUser(current_user.id)
    if form.created_articles.data:
        return redirect(f'/created_articles')
    if form.exit.data:
        logout_user()
        return redirect('/')
    return render_template('profile_check.html', name=current_user.name, form=form, current_user=current_user,
                           user_id=user.id)


def getUser(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(users.User).filter(users.User.id == user_id).first()
    return user


@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile_user(user_id):
    form = ProfileView()
    user = getUser(user_id)
    if form.created_articles.data:
        return redirect(f'/created_articles/{user.id}')
    if form.exit.data:
        logout_user()
        return redirect('/')
    return render_template('profile_check.html', name=user.name, form=form, current_user=current_user, user_id=user_id)


@app.route('/created_articles/<user_id>', methods=['GET', 'POST'])
def show_user_articles(user_id):
    user_articles = getUserArticles(user_id)
    if request.method == 'POST':
        article_id = request.form.get('id')
        return redirect(f'/articles/{article_id}/reading')
    if not user_articles:
        return 'Пользователь не создал ни одного теста'
    return render_template('all_articles.html', articles=user_articles, current_user=current_user,
                           title=f'Статьи пользователя {current_user.name}')


def getUserArticles(user_id):
    db_sess = db_session.create_session()
    user_articles = db_sess.query(articles.Articles).filter(articles.Articles.user_id == user_id).all()
    return user_articles


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
