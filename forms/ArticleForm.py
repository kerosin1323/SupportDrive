from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class CreatingArticleDataForm(FlaskForm):
    countries = ['Иномарка', 'Россия', 'Китай']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Страна производителя', choices=countries)
    photo = FileField('Добавить обложку')
    describe = TextAreaField('Описание')
    create = SubmitField('Создать')


class CommentsArticle(FlaskForm):
    text = TextAreaField()
