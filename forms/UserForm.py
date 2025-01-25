from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    register = SubmitField('Регистрация')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    username = StringField('Никнейм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    to_login = SubmitField('Вход')
    submit = SubmitField('Создать')


class ProfileView(FlaskForm):
    created_articles = SubmitField('Созданные статьи')
    exit = SubmitField('Выйти')
    add_data = SubmitField('Изменить')
    photo = FileField('Добавить фото')


class DescriptionProfile(FlaskForm):
    description = StringField('Описание')
    contacts = StringField('Контакты')
    create = SubmitField('Создать')
    photo = FileField('Изменить фото')
    name = StringField('Изменить имя')