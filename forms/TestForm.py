from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class MakingTestForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    category = StringField('Категория', validators=[DataRequired()])
    describe = StringField('Описание')
    photo = FileField('Фото', validators=[DataRequired()])
    add_question = SubmitField('+ Добавить вопрос +')
    create = SubmitField('Создать')


class MakingQuestion(FlaskForm):
    photo = FileField('Фото (600x600)')
    question = StringField('Текст вопроса')
    describe = StringField('Описание (Необязательно)')
    add_answer = SubmitField('+ Добавить вариант ответа +')

