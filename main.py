from flask import Flask, render_template
from data import db_session
from forms.make_test_form import MakingTestForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/make_test', methods=['GET', 'POST'])
def make_test():
    form = MakingTestForm()
    return render_template('make_test.html', title='Создание теста', form=form)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()