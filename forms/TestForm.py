from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class MakingTestForm(FlaskForm):
    dropdown_list = ['Фильмы', 'Спорт', 'Еда', 'Игры', 'Музыка', 'Наука', 'Техника']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Категория', choices=dropdown_list, default=1)
    describe = TextAreaField('Описание')
    photo = FileField('Фото', validators=[DataRequired()])
    add_question = SubmitField('+ Добавить вопрос +')
    create = SubmitField('Создать')


class MakingQuestion(FlaskForm):
    photo = FileField('Фото (600x600)')
    question = StringField('Текст вопроса')
    describe = StringField('Описание (Необязательно)')
    add_answer = SubmitField('+ Добавить вариант ответа +')

