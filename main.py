from flask import Flask, render_template, redirect
from data import db_session, tests, users
from forms.TestForm import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/', methods=['GET', 'POST'])
def index():
    form = MainForm()
    if form.make_test.data:
        return redirect('/make_test')
    elif form.take_test.data:
        return redirect('/take_test')
    return render_template('index.html', form=form)


@app.route('/take_test', methods=['GET', 'POST'])
def take_test():
    return 'Страница в разработке'


@app.route('/make_test', methods=['GET', 'POST'])
def make_test():
    form = MakingTestForm()
    if form.validate_on_submit():
        test = tests.Tests()
        test.name = form.name.data
        test.category = form.category.data
        test.photo = 'xxx'
        test.about = form.describe.data
        test.questions = ''
        db_sess = db_session.create_session()
        db_sess.add(test)
        db_sess.commit()
        test_id = test.id
        return redirect(f'/create_question/1/{test_id}')
    return render_template('make_test.html', title='Создание теста', form=form)


@app.route('/create_question/<number>/<test_id>', methods=['GET', "POST"])
def create_question(number, test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(tests.Tests).filter(tests.Tests.id == test_id).first()
    form = MakingQuestion()
    if form.validate_on_submit() and form.add_question.data:
        checks = (form.check_right1.data, form.check_right2.data, form.check_right3.data, form.check_right4.data)
        variants = (form.answer1.data, form.answer2.data, form.answer3.data, form.answer4.data)
        #test.questions[f'{number}'] = {'name': form.question.data,
                                       #'answers': {variants[0]: checks[0],
                                                                               #variants[1]: checks[1],
                                                                               #variants[2]: checks[2],
                                                                              # variants[3]: checks[3]}}
        return redirect(f'/create_question/{number + 1}?{test_id}')
    if form.validate_on_submit() and form.create.data:
        checks = (form.check_right1.data, form.check_right2.data, form.check_right3.data, form.check_right4.data)
        variants = (form.answer1.data, form.answer2.data, form.answer3.data, form.answer4.data)
        #test.questions[f'{number}'] = {'name': form.question.data,
                                       #'answers': {variants[0]: checks[0],
                                                                               #variants[1]: checks[1],
                                                                               #variants[2]: checks[2],
                                                                               #variants[3]: checks[3]}}
        return redirect('/')
    return render_template('make_question.html', form=form, number=number)



def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()