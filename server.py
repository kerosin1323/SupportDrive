from data.functions import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '1323'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
app.config['UPLOAD_FOLDER'] = './static/images'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(users.Users).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    popular_articles = get_on_category()
    return render_template('index.html', all_news=popular_articles, top_articles=get_top(), data=get_article_data(popular_articles), articles=popular_articles, leaders=get_leaders())


@app.route('/all/<category>', methods=['GET', 'POST'])
def all_category(category):
    get_articles = get_on_category(category)
    return render_template('all_articles.html', data=get_article_data(get_articles), articles=get_articles, current_user=current_user)


@app.route('/search/<text>', methods=['GET', 'POST'])
def search(text):
    found_articles = find(str(text))
    return render_template('all_articles.html', data=get_article_data(found_articles), articles=found_articles, current_user=current_user)


@app.route('/delete_article/<article_id>', methods=['GET'])
def delete_article(article_id):
    delete(article_id)
    return redirect(request.referrer)


@app.route('/all/<category>', methods=['GET', 'POST'])
def popular_category_articles(category):
    return render_template('index.html', articles=get_on_category(category))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.form.get('close'):
        return redirect('/')
    elif form.validate_on_submit():
        if is_email_already_exist(form.email.data):
            return render_template('register.html', form=form, message="Такая почта уже есть")
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
    right_email = check_email_and_login_user(prev, email_form.email_password.data, email)
    if right_email == 'True':
        return redirect('/')
    return render_template('email.html', form=email_form, message=(right_email if email_form.submit.data else ''))


@app.route('/read/<article_id>', methods=['GET', 'POST'])
def reading_article(article_id):
    add_reading(article_id)
    make_comment = request.form.get('comment')
    comment_text = request.form.get('comment_input')
    to_answer = request.form.get('to_answer')
    make_answer = request.form.get('make_answer')
    answer_text = request.form.get('answer_input')
    if make_answer and answer_text != '':
        create_comment(answer_text, article_id, make_answer)
    if make_comment and comment_text != '':
        create_comment(comment_text, article_id, None)
    current_article = get_article(article_id)
    creator = get_user(current_article.user_id)
    all_comments = get_comments(article_id)
    data_comments = get_comment_data(all_comments)
    mark = request.form.get('mark') or 0
    comment_make_mark = request.form.get('comment_mark')
    if request.form.get('to_subscribe'):
        subscribe(creator.id)
    if comment_make_mark:
        comment_id, comment_mark = comment_make_mark.split(',')
        mark_comment(comment_id, int(comment_mark))
    article_mark = mark_article(article_id, int(mark))
    return render_template('reading_article.html', time=text_delta(datetime.datetime.now() - current_article.created_date),
                           is_subscribed=check_subscribe(creator.id), to_answer=to_answer, amount_comments=len(all_comments),
                           article=current_article, current_user=current_user, user=creator, all_comments=all_comments,
                           data_comments=data_comments, mark=int(article_mark))


@app.route('/create_article', methods=['GET', 'POST'])
def creating_article():
    form = CreatingArticleDataForm()
    data = request.form.get('input')
    if form.create.data and data != '' and form.validate_on_submit():
        create_article(data, form, current_user.id, app)
        return redirect('/')
    return render_template('write_article.html', current_user=current_user, form=form)


@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile_user(user_id):
    form = ProfileView()
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
    if form.create.data:
        add_user_data(form, user_id, app)
        return redirect(f'/profile/{user_id}')
    return render_template('profile_data.html', form=form)


if __name__ == '__main__':
    app.run()
