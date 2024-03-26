from flask import Flask, render_template
from data import db_session, tests, users
from forms.TestForm import MakingTestForm, MakingQuestion

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/make_test', methods=['GET', 'POST'])
def make_test():
    global number
    form = MakingTestForm()
    dropdown_list = ['Фильмы', 'Спорт', 'Еда', 'Игры', 'Музыка', 'Наука', 'Техника']
    if form.add_question.data:
        number += 1
        print(number, form.add_question.data)
        form_question = MakingQuestion()
        return render_template('make_question.html', number=number, form=form, form_question=form_question)
    return render_template('make_test.html', title='Создание теста', form=form, dropdown_list=dropdown_list)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    number = 0
    main()