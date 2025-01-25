from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class CreatingArticleDataForm(FlaskForm):
    marks = ['BMW', 'Mercedes']
    building = ['Легковые', 'Грузовые', 'Электро']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Строение', choices=building)
    country = SelectField('Страна', choices=countries)
    mark = SelectField('Марка', choices=marks)
    key_words = StringField('Ключевые слова', validators=[DataRequired()])
    photo = FileField('Добавить обложку')
    back = SubmitField('Назад')
    describe = TextAreaField('Описание')
    create = SubmitField('Создать')


class CommentsArticle(FlaskForm):
    text = TextAreaField()