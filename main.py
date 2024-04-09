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
    test = db_sess.query(tests.Tests).filter(tests.Tests.category == trans_dict[category]).first()
    if request.method == 'POST':
        return redirect(f'/take_test/{test.id}/1')
    return render_template('start_test.html', test=test)


@app.route('/take_test/<test_id>/<question>', methods=['GET', 'POST'])
def take_test(test_id, question):
    right_answers = session.get('right_answers', 0)
    db_sess = db_session.create_session()
    test = db_sess.query(tests.Tests).filter(tests.Tests.id == test_id).first()
    data = json.loads(test.questions)[question]
    if request.method == 'POST' and int(question) <= len(data):
        print(request.form.items())
        if request.form == [i for i, k in data['answers'].items() if k][0]:
            right_answers += 1
        return redirect(f'/take_test/{test_id}/{int(question) + 1}')
    if int(question) <= len(data):
        return render_template('questions.html', number_question=question, name=data['name'], answer=[i for i in data['answers']])
    return render_template('finish_test.html', right_answers=right_answers, all_questions=len(data), percent=int(right_answers/len(data)*100), )



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
        print(prev_questions, questions_str)
        test.questions = json.dumps({**prev_questions, **questions_str}, ensure_ascii=False)
        db_sess.commit()
        if form.add_question.data:
            return redirect(f'/create_question/{test_id}/{int(number) + 1}')
        elif form.create.data:
            return redirect('/')
    return render_template('make_question.html', form=form, number=number)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
