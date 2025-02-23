import datetime
from flask_login import *
from flask import *
from data import db_session, functions, users
from forms.ArticleForm import *
from forms.UserForm import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['UPLOAD_FOLDER'] = './static/images'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/blogs.sql")
article = functions.Article()
user = functions.User()
comment = functions.Comment()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(users.Users).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    to_read = article.clickedToRead()
    if to_read:
        return redirect(f'/article/{to_read}/read')
    article.toDelete()
    leaders = user.getLeaders()
    popular_articles = article.getCategory()
    data = article.getData(popular_articles)
    return render_template('index.html', data=data, articles=popular_articles, leaders=leaders)


@app.route('/all/<category>', methods=['GET', 'POST'])
def all_category(category):
    to_read = article.clickedToRead()
    if to_read:
        return redirect(f'/article/{to_read}/read')
    article.toDelete()
    get_articles = article.getCategory(category)
    articles_data = article.getData(get_articles)
    return render_template('all_articles.html', data=articles_data, articles=get_articles, current_user=current_user)


@app.route('/search', methods=['GET', 'POST'])
def search():
    to_read = article.clickedToRead()
    if to_read:
        return redirect(f'/article/{to_read}/read')
    article.toDelete()
    text = str(request.form.get('search'))
    found_articles = article.find(text)
    articles_data = article.getData(found_articles)
    return render_template('all_articles.html', data=articles_data, articles=found_articles, current_user=current_user, search=True)


@app.route('/all/<category>', methods=['GET', 'POST'])
def popular_category_articles(category):
    to_read = article.clickedToRead()
    if to_read:
        return redirect(f'/article/{to_read}/read')
    article.toDelete()
    popular_articles = article.getCategory(category)
    return render_template('index.html', articles=popular_articles)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.to_login.data:
        return redirect('/login')
    elif form.validate_on_submit():
        if user.alreadyExist(form.username.data):
            return render_template('register.html', form=form, message="Такой пользователь уже есть")
        user.create(form)
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.register.data:
        return redirect('/register')
    elif form.validate_on_submit():
        user.checkAndLogin(form.username.data, form.password.data)
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
        all_comments = comment.add(answer_text, article_id, make_answer)
    if make_comment and comment_text != '':
        all_comments = comment.add(comment_text, article_id, None)
    the_article = article.get(article_id)
    creator = user.get(the_article.user_id)
    all_comments = comment.get(article_id)
    data_comments = comment.getData(all_comments)
    mark = request.form.get('mark')
    comment_make_mark = request.form.get('comment_mark')
    time = functions.text_delta(datetime.datetime.now() - the_article.created_date)
    if comment_make_mark:
        comment_id, comment_mark = comment_make_mark.split(',')
        comment.addMark(comment_id, comment_mark)
    if mark:
        article.addMark(article_id, int(mark))
    if request.form.get('to_subscribe'):
        user.subscribeOn(creator.id)
    is_subscribed = user.checkSubscribe(creator.id)
    return render_template('reading_article.html', time=time, is_subscribed=is_subscribed,
                           to_answer=to_answer, amount_comments=len(all_comments), time_now=datetime.datetime.now(),
                           article=article, current_user=current_user, user=creator, all_comments=all_comments)


@app.route('/create_article', methods=['GET', 'POST'])
def create_article():
    form = CreatingArticleDataForm()
    data = request.form.get('input')
    if form.create.data and data != '' and form.validate_on_submit():
        article.add(data, form, current_user.id, app)
        return redirect('/')
    return render_template('write_article.html', current_user=current_user, form=form)


@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile_user(user_id):
    form = ProfileView()
    to_read = article.clickedToRead()
    if to_read:
        return redirect(f'/article/{to_read}/read')
    article.toDelete()
    if form.created_articles.data:
        show_articles = article.getOnUser(user_id)
    elif form.follow.data:
        show_articles = article.getFollowed(user_id)
    else:
        show_articles = []
    articles_data = article.getData(show_articles)
    all_subscriptions = user.getSubscriptions(user_id)
    if request.form.get('to_subscribe'):
        user.subscribeOn(user_id)
    if form.add_data.data:
        return redirect(f'/profile_data/{user_id}')
    if form.exit.data:
        logout_user()
        return redirect('/')
    is_subscribed = user.checkSubscribe(user_id)
    return render_template('profile_check.html', add_articles=show_articles, articles_data=articles_data, is_subscribed=is_subscribed,
                           form=form, current_user=current_user, user=user.get(user_id), all_subscriptions=all_subscriptions)


@app.route('/profile_data/<user_id>', methods=['GET', 'POST'])
def descript_user(user_id):
    form = DescriptionProfile()
    if form.create.data:
        user.addData(form, user_id)
        return redirect(f'/profile/{user_id}')
    return render_template('profile_data.html', form=form)


if __name__ == '__main__':
    app.run()
