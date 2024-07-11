from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    register = SubmitField('Зарегестрироваться')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    to_login = SubmitField('Войти в аккаунт')
    submit = SubmitField('Создать')


class MainForm(FlaskForm):
    make_test = SubmitField('Создать тест')
    take_test = SubmitField('Пройти тест')


class MakingTestForm(FlaskForm):
    dropdown_list = ['Фильмы', 'Спорт', 'Еда', 'Игры', 'Музыка', 'Наука', 'Технологии', 'Другое']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Категория', choices=dropdown_list, default=1)
    describe = TextAreaField('Описание')
    add_photo = FileField('Добавить фото')
    add_question = SubmitField('+ Добавить вопрос +')


class ChangingTestForm(FlaskForm):
    dropdown_list = ['Фильмы', 'Спорт', 'Еда', 'Игры', 'Музыка', 'Наука', 'Технологии', 'Другое']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Категория', choices=dropdown_list, default=1)
    describe = TextAreaField('Описание')
    add_photo = FileField('Добавить фото')
    add_question = SubmitField('+ Изменить вопрос +')


class CategoryForm(FlaskForm):
    films = SubmitField('Фильмы')
    sport = SubmitField('Спорт')
    foods = SubmitField('Еда')
    games = SubmitField('Игры')
    music = SubmitField('Музыка')
    science = SubmitField('Наука')
    tech = SubmitField('Технологии')
    others = SubmitField('Другое')


class MakingQuestion(FlaskForm):
    question = StringField('Текст вопроса', validators=[DataRequired()])
    add_question = SubmitField('+ Добавить вопрос +')
    answer1 = StringField('Ответ', validators=[DataRequired()])
    check_right1 = BooleanField('Верный ответ')
    answer2 = StringField('Ответ', validators=[DataRequired()])
    check_right2 = BooleanField('Верный ответ')
    answer3 = StringField('Ответ', validators=[DataRequired()])
    check_right3 = BooleanField('Верный ответ')
    answer4 = StringField('Ответ', validators=[DataRequired()])
    check_right4 = BooleanField('Верный ответ')
    add_photo = FileField('Добавить фото')
    create = SubmitField('Создать')


class ChangingQuestion(FlaskForm):
    question = StringField('Текст вопроса', validators=[DataRequired()])
    add_question = SubmitField('+ Изменить вопрос +')
    answer1 = StringField('Ответ', validators=[DataRequired()])
    check_right1 = BooleanField('Верный ответ')
    answer2 = StringField('Ответ', validators=[DataRequired()])
    check_right2 = BooleanField('Верный ответ')
    answer3 = StringField('Ответ', validators=[DataRequired()])
    check_right3 = BooleanField('Верный ответ')
    answer4 = StringField('Ответ', validators=[DataRequired()])
    check_right4 = BooleanField('Верный ответ')
    create = SubmitField('Сохранить')


class ProfileView(FlaskForm):
    created_tests = SubmitField('Созданные тесты')
    exit = SubmitField('Выйти')
