import datetime
from flask_login import *
from flask import *
from data import db_session, articles, users, comments
from forms.ArticleForm import *
from forms.UserForm import *


app = Flask(__name__)
all_articles = articles.Article()
all_users = users.User()
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['UPLOAD_FOLDER'] = './static/images'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/blogs.sql")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(users.User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    leaders = all_users.getLeaders()
    popular_articles = all_articles.getCategory()
    data = all_articles.getData(popular_articles)
    all_articles.clicked()
    return render_template('index.html', data=data, articles=popular_articles, leaders=leaders)


@app.route('/all/<category>', methods=['GET', 'POST'])
def all_category(category):
    get_articles = all_articles.getCategory(category)
    articles_data = all_articles.getData(get_articles)
    all_articles.clicked()
    return render_template('all_articles.html', link=category, data=articles_data, articles=get_articles, current_user=current_user)


@app.route('/search', methods=['GET', 'POST'])
def search():
    text = str(request.form.get('search'))
    found_articles = all_articles.find(text)
    articles_data = all_articles.getData(found_articles)
    all_articles.clicked()
    return render_template('all_articles.html', data=articles_data, articles=found_articles, current_user=current_user, search=True)


@app.route('/all/<category>', methods=['GET', 'POST'])
def popular_category_articles(category):
    popular_articles = all_articles.getCategory(category)
    all_articles.clicked()
    return render_template('index.html', articles=popular_articles)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.to_login.data:
        return redirect('/login')
    elif form.validate_on_submit():
        if all_users.alreadyExist(form.username.data):
            return render_template('register.html', form=form, message="Такой пользователь уже есть")
        all_users.create(form)
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.register.data:
        return redirect('/register')
    elif form.validate_on_submit():
        all_users.checkAndLogin(form.username.data, form.password.data)
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form, current_user=current_user)


@app.route('/article/<article_id>/read', methods=['GET', 'POST'])
def reading_article(article_id):
    make_comment = request.form.get('comment')
    comment_text = request.form.get('comment_input')
    to_answer = request.form.get('to_answer')
    make_answer = request.form.get('make_answer')
    answer_text = request.form.get('answer_input')
    if make_answer and answer_text != '':
        all_comments = comments.Comment().add(answer_text, article_id, make_answer)
    if make_comment and comment_text != '':
        all_comments = comments.Comment().add(comment_text, article_id, None)
    article = all_articles.get(article_id)
    user = all_users.get(article.user_id)
    all_comments = comments.Comment().get(article_id)
    data_comments = comments.Comment().getData(all_comments)
    mark = request.form.get('mark')
    comment_make_mark = request.form.get('comment_mark')
    time = articles.text_delta(datetime.datetime.now() - article.created_date)
    if comment_make_mark:
        comment_id, comment_mark = comment_make_mark.split(',')
        comments.Comment().addMark(comment_id, comment_mark)
    if mark:
        all_articles.addMark(article_id, int(mark))
    if request.form.get('to_subscribe'):
        all_users.subscribeOn(user.id)
    is_subscribed = all_users.checkSubscribe(user.id)
    return render_template('reading_article.html', time=time, is_subscribed=is_subscribed,
                           to_answer=to_answer, amount_comments=len(all_comments), time_now=datetime.datetime.now(),
                           article=article, current_user=current_user, user=user, all_comments=all_comments)


@app.route('/create_article', methods=['GET', 'POST'])
def create_article():
    form = CreatingArticleDataForm()
    data = request.form.get('input')
    if form.create.data and data != '' and form.validate_on_submit():
        all_articles.add(data, form, current_user.id)
        return redirect('/')
    return render_template('write_article.html', current_user=current_user, form=form)


@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile_user(user_id):
    form = ProfileView()
    if form.created_articles.data:
        show_articles = all_articles.getOnUser(user_id)
    elif form.follow.data:
        show_articles = all_articles.getFollowed(user_id)
    else:
        show_articles = []
    articles_data = all_articles.getData(show_articles)
    all_subscriptions = all_users.getSubscriptions(user_id)
    if request.form.get('to_subscribe'):
        all_users.subscribeOn(user_id)
    if form.add_data.data:
        return redirect(f'/profile_data/{user_id}')
    all_articles.clicked()
    if form.exit.data:
        logout_user()
        return redirect('/')
    is_subscribed = all_users.checkSubscribe(user_id)
    return render_template('profile_check.html', add_articles=show_articles, articles_data=articles_data, is_subscribed=is_subscribed,
                           form=form, current_user=current_user, user=all_users.get(user_id), all_subscriptions=all_subscriptions)


@app.route('/profile_data/<user_id>', methods=['GET', 'POST'])
def descript_user(user_id):
    form = DescriptionProfile()
    if form.create.data:
        all_users.addData(form, user_id)
        return redirect(f'/profile/{user_id}')
    return render_template('profile_data.html', form=form)


if __name__ == '__main__':
    app.run()
