from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    register = SubmitField('Зарегестрироваться')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    username = StringField('Никнейм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    to_login = SubmitField('Войти в аккаунт')
    submit = SubmitField('Создать')


class ProfileView(FlaskForm):
    created_articles = SubmitField('Созданные статьи')
    exit = SubmitField('Выйти')
