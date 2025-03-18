from data.functions import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '1323'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['UPLOAD_FOLDER'] = './static/images'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(users.Users).get(user_id)

def base_methods():
    read = to_read()
    to_search = request.form.get('to_search')
    if to_search:
        return redirect(f'/search/{to_search}')
    if read:
        return redirect(f'/article/{read}/read')
    delete()


@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    base_methods()
    popular_articles = get_on_category()
    return render_template('index.html', top_articles=get_top(), data=get_article_data(popular_articles), articles=popular_articles, leaders=get_leaders())


@app.route('/all/<category>', methods=['GET', 'POST'])
def all_category(category):
    base_methods()
    get_articles = get_on_category(category)
    return render_template('all_articles.html', data=get_article_data(get_articles), articles=get_articles, current_user=current_user)


@app.route('/search/<text>', methods=['GET', 'POST'])
def search(text):
    base_methods()
    found_articles = find(str(text))
    return render_template('all_articles.html', data=get_article_data(found_articles), articles=found_articles, current_user=current_user)


@app.route('/all/<category>', methods=['GET', 'POST'])
def popular_category_articles(category):
    base_methods()
    return render_template('index.html', articles=get_on_category(category))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.login.data:
        return redirect('/login')
    if request.form.get('close'):
        return redirect('/')
    elif form.validate_on_submit():
        if is_exist(form.email.data):
            return render_template('register.html', form=form, message="Такой пользователь уже есть")
        password = send_password(form.email.data)
        session[form.email.data] = (form.data, password)
        return redirect(f'/check_email/$email={form.email.data}$prev=reg')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.register.data:
        return redirect('/register')
    if request.form.get('close'):
        return redirect('/')
    elif form.validate_on_submit():
        if check(form.email.data, form.password.data):
            password = send_password(form.email.data)
            session[form.email.data] = (form.data, password)
            return redirect(f'/check_email/$email={form.email.data}$prev=log')
        return render_template('login.html', message="Неправильная почта или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form, current_user=current_user)


@app.route('/check_email/$email=<email>$prev=<prev>', methods=['GET', 'POST'])
def check_email(email, prev):
    email_form = EmailForm()
    data = session[email][0]
    parse_password = session[email][1]
    password = email_form.email_password.data
    if prev == 'reg' and str(password) == str(parse_password):
        create_user(data)
        return redirect('/')
    elif prev == 'log' and str(password) == str(parse_password):
        user_log = get_on_email(email)
        login_user(user_log)
        return redirect('/')
    elif password and str(password) != str(parse_password):
        return render_template('email.html', message="Неправильный пароль", form=email_form)
    return render_template('email.html', form=email_form)


@app.route('/article/<article_id>/read', methods=['GET', 'POST'])
def reading_article(article_id):
    make_comment = request.form.get('comment')
    comment_text = request.form.get('comment_input')
    to_answer = request.form.get('to_answer')
    make_answer = request.form.get('make_answer')
    answer_text = request.form.get('answer_input')
    base_methods()
    if make_answer and answer_text != '':
        create_comment(answer_text, article_id, make_answer)
    if make_comment and comment_text != '':
        create_comment(comment_text, article_id, None)
    current_article = get_article(article_id)
    creator = get_user(current_article.user_id)
    all_comments = get_comments(article_id)
    answers_comments = get_answers(all_comments)
    data_comments = get_comment_data(all_comments)
    mark = request.form.get('mark')
    comment_make_mark = request.form.get('comment_mark')
    time = text_delta(datetime.datetime.now() - current_article.created_date)
    if request.form.get('to_subscribe'):
        subscribe(creator.id)
    if comment_make_mark:
        comment_id, comment_mark = comment_make_mark.split(',')
        mark_comment(comment_id, int(comment_mark))
    if mark:
        mark_article(article_id, int(mark))
    is_subscribed = check_subscribe(creator.id)
    return render_template('reading_article.html', time=time, is_subscribed=is_subscribed,
                           to_answer=to_answer, amount_comments=len(all_comments), answers_comments=answers_comments,
                           article=current_article, current_user=current_user, user=creator, all_comments=all_comments,
                           data_comments=data_comments)


@app.route('/create_article', methods=['GET', 'POST'])
def create_article():
    form = CreatingArticleDataForm()
    data = request.form.get('input')
    base_methods()
    if form.create.data and data != '' and form.validate_on_submit():
        create_article(data, form, current_user.id, app)
        return redirect('/')
    return render_template('write_article.html', current_user=current_user, form=form)


@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile_user(user_id):
    form = ProfileView()
    base_methods()
    if form.created_articles.data:
        show_articles = get_article_from_user(user_id)
    elif form.follow.data:
        show_articles = get_followed(user_id)
    else:
        show_articles = []
    articles_data = get_article_data(show_articles)
    if form.subscribe.data:
        all_subscriptions = get_subscriptions(user_id)
    else:
        all_subscriptions = []
    if request.form.get('to_subscribe'):
        subscribe(user_id)
    if form.add_data.data:
        return redirect(f'/profile_data/{user_id}')
    if form.exit.data:
        logout_user()
        return redirect('/')
    is_subscribed = check_subscribe(user_id)
    return render_template('profile_check.html', show_articles=show_articles, articles_data=articles_data,
                           is_subscribed=is_subscribed,
                           form=form, current_user=current_user, user=get_user(user_id),
                           all_subscriptions=all_subscriptions)


@app.route('/profile_data/<user_id>', methods=['GET', 'POST'])
def change_data_user(user_id):
    form = DescriptionProfile()
    base_methods()
    if form.create.data:
        add_user_data(form, user_id, app)
        return redirect(f'/profile/{user_id}')
    return render_template('profile_data.html', form=form)


if __name__ == '__main__':
    app.run()
