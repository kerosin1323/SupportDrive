from flask import Flask, render_template, request
from data import db_session, tests, users
from forms.TestForm import MakingTestForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/make_test', methods=['GET', 'POST'])
def make_test():
    form = MakingTestForm()
    dropdown_list = ['Фильмы', 'Спорт', 'Еда', 'Игры', 'Музыка', 'Наука', 'Техника']
    return render_template('make_test.html', title='Создание теста', form=form, dropdown_list=dropdown_list)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()