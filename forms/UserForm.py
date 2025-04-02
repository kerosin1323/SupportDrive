from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Создать')


class EmailForm(FlaskForm):
    email_password = StringField('Код', validators=[DataRequired()])
    submit = SubmitField('Проверить')


class ProfileView(FlaskForm):
    created_articles = SubmitField('Созданные статьи')
    exit = SubmitField('Выйти')
    add_data = SubmitField('Изменить')
    follow = SubmitField('Избранные')
    subscribe = SubmitField('Подписки')


class DescriptionProfile(FlaskForm):
    description = StringField('Описание')
    contacts = StringField('Контакты')
    create = SubmitField('Изменить')
    photo = FileField('Изменить фото')
    name = StringField('Изменить имя')

