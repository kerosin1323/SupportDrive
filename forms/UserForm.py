from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    login_admin = SubmitField('Войти как админ')
    register = SubmitField('Регистрация')
    submit = SubmitField('Войти')


class LoginAdmin(LoginForm):
    admin_password = StringField('Админ-Пароль', validators=[DataRequired()])
    login_user = SubmitField('Войти как пользователь')


class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    username = StringField('Никнейм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    register_admin = SubmitField('Стать админом')
    to_login = SubmitField('Вход')
    submit = SubmitField('Создать')


class RegisterAdmin(RegisterForm):
    register_user = SubmitField('Стать пользователем')


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