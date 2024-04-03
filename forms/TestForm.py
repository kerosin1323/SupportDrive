from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class MainForm(FlaskForm):
    make_test = SubmitField('Создать тест')
    take_test = SubmitField('Пройти тест')


class MakingTestForm(FlaskForm):
    dropdown_list = ['Фильмы', 'Спорт', 'Еда', 'Игры', 'Музыка', 'Наука', 'Техника']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Категория', choices=dropdown_list, default=1)
    describe = TextAreaField('Описание')
    photo = FileField('Фото', validators=[DataRequired()])
    add_question = SubmitField('+ Добавить вопрос +')


class MakingQuestion(FlaskForm):
    photo = FileField('Фото (600x600)')
    question = StringField('Текст вопроса')
    add_question = SubmitField('+ Добавить вопрос +')
    answer1 = StringField('Ответ')
    check_right1 = BooleanField('Верный ответ')
    answer2 = StringField('Ответ')
    check_right2 = BooleanField('Верный ответ')
    answer3 = StringField('Ответ')
    check_right3 = BooleanField('Верный ответ')
    answer4 = StringField('Ответ')
    check_right4 = BooleanField('Верный ответ')
    create = SubmitField('Создать')
