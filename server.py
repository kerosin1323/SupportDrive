from data.functions import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '1323'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
app.config['UPLOAD_FOLDER'] = './static/images'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id: int):
    return db_sess.query(users.Users).get(user_id)


@app.get('/')
@app.get('/all/<string:category>')
def welcome_page(category=None):
    popular_articles = get_on_category(category)
    all_news = get_all_news()
    return render_template('index.html', all_news=all_news, data_news=get_article_data(all_news), top_articles=get_top(), data=get_article_data(popular_articles), articles=popular_articles, leaders=get_leaders())


@app.get('/forum')
def forum():
    popular_questions = get_popular_questions()
    top_experts = get_experts()
    return render_template('forum.html', data=get_question_data(popular_questions), questions=popular_questions, experts=top_experts)


@app.route('/search/<string:text>', methods=['GET', 'POST'])
def search(text: str):
    found_articles = find(str(text))
    return render_template('index.html', data=get_article_data(found_articles), articles=found_articles, current_user=current_user)


@app.get('/filter/time=<string:filter_time>$type=<string:filter_type>')
def filter_articles(filter_time: str, filter_type: str):
    filtered_articles = sort_articles_by_time_and_type(filter_time, filter_type)
    all_news = get_all_news()
    return render_template('index.html', all_news=all_news, data_news=get_article_data(all_news), top_articles=get_top(), data=get_article_data(filtered_articles), articles=filtered_articles, leaders=get_leaders())


@app.get('/filter_questions/time=<string:filter_time>$type=<string:filter_type>')
def filter_questions(filter_time: str, filter_type: str):
    filtered_articles = sort_questions_by_time_and_type(filter_time, filter_type)
    top_experts = get_experts()
    return render_template('forum.html', data=get_question_data(filtered_articles), questions=filtered_articles, experts=top_experts)


@app.get('/delete_article/<int:article_id>')
def delete_article(article_id: int):
    delete(article_id)
    return redirect(request.referrer)


@app.get('/delete_question/<int:question_id>')
def delete_question(question_id: int):
    delete_question(question_id)
    return redirect(request.referrer)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        check_data = check_data_and_register_user(form)
        if check_data:
            return render_template('register.html', form=form, message=check_data)
        return redirect(f'/check_email/$email={form.email.data}$prev=reg')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        check_data = check_data_and_send_email(form)
        if check_data:
            return render_template('login.html', message=check_data, form=form)
        return redirect(f'/check_email/$email={form.email.data}$prev=log')
    return render_template('login.html', title='Авторизация', form=form, current_user=current_user)


@app.route('/check_email/$email=<string:email>$prev=<string:prev>', methods=['GET', 'POST'])
def check_email(email: str, prev: str):
    email_form = EmailForm()
    right_email = check_email_and_login_user(prev, email_form.email_password.data, email)
    if right_email == 'True':
        return redirect('/')
    return render_template('email.html', form=email_form, message=(right_email if email_form.submit.data else ''))


@app.get('/add_reading/<int:article_id>')
def add_read(article_id: int):
    add_reading(article_id)
    return redirect(f'/read/{article_id}')


@app.get('/add_reading_question/<int:question_id>')
def add_read_question(question_id):
    add_reading_question(question_id)
    return redirect(f'/read_question/{question_id}')


@app.route('/read/<int:article_id>', methods=['GET', 'POST'])
def reading_article(article_id: int):
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
                           is_subscribed=check_subscribe(creator.id), to_answer=to_answer, short_amount_comments=short_form(len(all_comments)),
                           article=current_article, current_user=current_user, user=creator, all_comments=all_comments, short_mark=short_form(current_article.mark),
                           data_comments=data_comments, mark=int(article_mark), short_readings=short_form(current_article.readings))


@app.route('/read_question/<int:question_id>', methods=['GET', 'POST'])
def reading_question(question_id: int):
    make_answer = request.form.get('answer')
    answer_text = request.form.get('answer_input')
    right_answer = request.form.get('right_answer')
    false_answer = request.form.get('false_answer')
    if make_answer and answer_text != '':
        create_answer(answer_text, question_id)
    current_question = get_question(question_id)
    creator = get_user(current_question.user_id)
    all_answers = get_answers_on_question(question_id)
    data_answers = get_answers_data(all_answers)
    mark = request.form.get('mark') or 0
    answer_make_mark = request.form.get('answer_mark')
    if request.form.get('to_subscribe'):
        subscribe(creator.id)
    if answer_make_mark:
        answer_id, answer_mark = answer_make_mark.split(',')
        mark_answer(answer_id, int(answer_mark))
    if right_answer:
        make_right_answer(int(right_answer))
    if false_answer:
        make_false_answer(int(false_answer))
    question_mark = mark_question(question_id, int(mark))
    return render_template('reading_question.html', time=text_delta(datetime.datetime.now() - current_question.created_date),
                           is_subscribed=check_subscribe(creator.id), short_amount_answers=short_form(len(all_answers)),
                           question=current_question, current_user=current_user, user=creator, all_answers=all_answers, short_mark=short_form(current_question.mark),
                           data_answers=data_answers, mark=int(question_mark), short_readings=short_form(current_question.readings))


@app.route('/create_article', methods=['GET', 'POST'])
def creating_article():
    form = CreatingArticleDataForm()
    data = request.form.get('text')
    brand = request.form.get('brand')
    photo = request.files.get('file[]')
    if form.create.data and data != '' and form.validate_on_submit():
        check_data = check_article_data(form, data)
        if not check_data:
            create_article(data, form, current_user.id, app, brand, photo)
            return redirect('/')
        return render_template('write_article.html', current_user=current_user, form=form, all_brands=form.brand, message=check_data)
    return render_template('write_article.html', current_user=current_user, form=form, all_brands=form.brand)


@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    form = CreatingQuestionForm()
    data = request.form.get('text')
    brand = request.form.get('brand')
    if form.create.data and data != '' and form.validate_on_submit():
        check_data = check_question_data(form, data)
        if not check_data:
            create_question(data, form, current_user.id, brand)
            return redirect('/')
        return render_template('create_question.html', current_user=current_user, form=form, all_brands=form.brand, message=check_data)
    return render_template('create_question.html', current_user=current_user, form=form, all_brands=form.brand)


@app.route('/edit_article/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id: int):
    form = EditArticleForm()
    article = get_article(article_id)
    data = request.form.get('text')
    brand = request.form.get('brand')
    photo = request.files.get('file[]')
    if form.create.data and data != '' and form.validate_on_submit():
        check_data = check_article_data(form, data)
        if not check_data:
            change_article(data, form, article.id, app, brand, photo)
            return redirect('/')
        return render_template('edit_article.html', article=article, form=form, all_brands=form.brand, message=check_data)
    if request.method == 'GET':
        form.describe.data = article.describe
        form.category.data = article.categories
        form.body_category.data = article.body
    return render_template('edit_article.html', article=article, form=form, all_brands=form.brand)


@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id: int):
    form = EditQuestionForm()
    question = get_question(question_id)
    data = request.form.get('text')
    brand = request.form.get('brand')
    if form.create.data and data != '' and form.validate_on_submit():
        check_data = check_question_data(form, data)
        if not check_data:
            change_question(data, form, question.id, brand)
            return redirect('/')
        return render_template('edit_question.html', question=question, form=form, all_brands=form.brand, message=check_data)
    if request.method == 'GET':
        form.body_category.data = question.body
    return render_template('edit_question.html', question=question, form=form, all_brands=form.brand)


@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile_user(user_id: int):
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


@app.route('/profile_data/<int:user_id>', methods=['GET', 'POST'])
def change_data_user(user_id: int):
    form = DescriptionProfile()
    if form.create.data:
        add_user_data(form, user_id, app)
        return redirect(f'/profile/{user_id}')
    return render_template('profile_data.html', form=form)


if __name__ == '__main__':
    app.run()
