from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class CreatingArticleForm(FlaskForm):
    dropdown_list = ['Фильмы', 'Спорт', 'Еда', 'Игры', 'Музыка', 'Наука', 'Технологии', 'Другое']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Категория', choices=dropdown_list, default=1)
    describe = TextAreaField('Описание')
    add_photo = FileField('Добавить фото', validators=[DataRequired()])
    add_question = SubmitField('+ Добавить вопрос +')


class ChangingArticleForm(FlaskForm):
    dropdown_list = ['Фильмы', 'Спорт', 'Еда', 'Игры', 'Музыка', 'Наука', 'Технологии', 'Другое']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Категория', choices=dropdown_list, default=1)
    describe = TextAreaField('Описание')
    add_photo = FileField('Добавить фото', validators=[DataRequired()])
    add_question = SubmitField('+ Изменить вопрос +')


class ProfileView(FlaskForm):
    created_tests = SubmitField('Созданные тесты')
    exit = SubmitField('Выйти')
    delete = SubmitField('Удалить пользователя')
