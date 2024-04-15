import datetime

from flask import Flask, render_template, redirect, request, session
from data import db_session, tests, users
from forms.TestForm import *
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = MainForm()
    if form.make_test.data:
        return redirect('/make_test')
    elif form.take_test.data:
        return redirect('/choose_category')
    elif form.check_profile.data:
        profile_id = int(request.cookies.get("profile_id", 111))
        if profile_id:
            return redirect(f'/profile/{profile_id}')
        else:
            return redirect(f'/profile/{profile_id}')
            #  pass страница для авторизации
    return render_template('index.html', form=form)


@app.route('/choose_category', methods=['GET', 'POST'])
def choose_category():
    form = CategoryForm()
    if form.validate_on_submit():
        pressed = [i for i, k in form.data.items() if k][0]
        return redirect(f'/tests/{pressed}')
    return render_template('category.html', form=form)


@app.route('/tests/<category>', methods=['GET', 'POST'])
def show_all_tests(category):
    trans_dict = {'films': 'Фильмы', 'sport': 'Спорт', 'foods': 'еда', 'games': 'Игры', 'science': 'Наука',
                  'tech': 'Технологии', 'other': 'другое', 'music': 'Музыка'}
    db_sess = db_session.create_session()
    test = db_sess.query(tests.Tests).filter(tests.Tests.category == trans_dict[category]).all()
    if request.method == 'POST':
        test_id = request.form.get('id')
        return redirect(f'/tests/{test_id}/start')
    if not test:
        return 'Тестов с такой категорией пока нет'
    return render_template('all_tests.html', test=test)


@app.route('/tests/<test_id>/start', methods=['GET', 'POST'])
def start_test(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(tests.Tests).filter(tests.Tests.id == test_id).first()
    if request.method == 'POST':
        return redirect(f'/take_test/{test.id}/1')
    return render_template('start_test.html', test=test, mark=f'+{test.mark}' if test.mark > 0 else test.mark)


@app.route('/take_test/<test_id>/<question>', methods=['GET', 'POST'])
def take_test(test_id, question):
    mark = session['mark'] = session.get('mark', 0)
    right_answers = session.get('right_answers', 0)
    db_sess = db_session.create_session()
    test = db_sess.query(tests.Tests).filter(tests.Tests.id == test_id).first()
    data = json.loads(test.questions)
    if request.method == 'POST' and int(question) <= len(data):
        if [j for j, v in data[question]['answers'].items()][int(request.form.get('index'))] == [i for i, k in data[question]['answers'].items() if k][0]:
            session['right_answers'] = right_answers + 1
        return redirect(f'/take_test/{test_id}/{int(question) + 1}')
    if request.form.get('mark') == '+' and mark < 1:
        session['mark'] += 1
        mark += 1
    elif request.form.get('mark') == '-' and mark > -1:
        session['mark'] -= 1
        mark -= 1
    if int(question) <= len(data):
        return render_template('questions.html', number_question=question, name=data[question]['name'], answer=[i for i in data[question]['answers']])
    if request.form.get('exit') == '1':
        test.mark += mark
        db_sess.commit()
        session['right_answers'] = 0
        return redirect('/')
    return render_template('finish_test.html', right_answers=right_answers, all_questions=len(data), percent=int(right_answers/len(data)*100), mark=f'+{mark}' if mark == 1 else mark)


@app.route('/make_test', methods=['GET', 'POST'])
def make_test():
    form = MakingTestForm()
    if form.validate_on_submit():
        test = tests.Tests()
        test.name = form.name.data
        test.category = form.category.data
        test.photo = 'xxx'
        test.about = form.describe.data
        db_sess = db_session.create_session()
        db_sess.add(test)
        db_sess.commit()
        return redirect(f'/create_question/{test.id}/1')
    return render_template('make_test.html', title='Создание теста', form=form)


@app.route('/create_question/<test_id>/<number>', methods=['GET', "POST"])
def create_question(number, test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(tests.Tests).filter(tests.Tests.id == test_id).first()
    form = MakingQuestion()
    if form.validate_on_submit():
        checks = (form.check_right1.data, form.check_right2.data, form.check_right3.data, form.check_right4.data)
        variants = (form.answer1.data, form.answer2.data, form.answer3.data, form.answer4.data)
        questions_str = {f'{number}': {'name': form.question.data,
                                                  'answers': {variants[0]: checks[0],
                                                              variants[1]: checks[1],
                                                              variants[2]: checks[2],
                                                              variants[3]: checks[3]}}}
        try:
            prev_questions = json.loads(test.questions)
        except TypeError:
            prev_questions = {}
        test.questions = json.dumps({**prev_questions, **questions_str}, ensure_ascii=False)
        db_sess.commit()
        if form.add_question.data:
            return redirect(f'/create_question/{test_id}/{int(number) + 1}')
        elif form.create.data:
            return redirect('/')
    return render_template('make_question.html', form=form, number=number)


@app.route('/profile/<profile_id>', methods=['GET', 'POST'])
def open_profile(profile_id):
    form = ProfileView()
    if form.checked_tests.data:
        return redirect(f'/checked_tests/{profile_id}')
    if form.created_tests.data:
        return redirect(f'/created_tests/{profile_id}')
    return render_template('profile_check.html', name="name", checked_tests_count="chcount", percent="percent", form=form)  # name, chcount и percent позже сменим на имя с бд пользователей




def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
