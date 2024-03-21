from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class MakingTestForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    category = StringField('Категория', validators=[DataRequired()])
    describe = StringField('Описание')
    photo = FileField('Фото')
    add_question = SubmitField('+ Добавить вопрос +')
    create = SubmitField('Создать')