from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class CreatingArticleDataForm(FlaskForm):
    categories_list = ['Легковые', 'Грузовые', 'Электро', 'Китайские', 'Российские', 'Иномарки']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Категория', choices=categories_list)
    key_words = StringField('Ключевые слова', validators=[DataRequired()])
    photo = FileField('Добавить обложку')
    back = SubmitField('Назад')
    describe = TextAreaField('Описание')
    create = SubmitField('Создать')


class ChangingArticleForm(FlaskForm):
    categories_list = ['Легковые', 'Грузовые', 'Электро', 'Китайские', 'Российские', 'Иномарки']
    name = StringField('Название')
    category = SelectField('Категория', choices=categories_list)
    key_words = StringField('Ключевые слова')
    photo = FileField('Добавить обложку')
    back = SubmitField('Назад')
    create = SubmitField('Создать')
