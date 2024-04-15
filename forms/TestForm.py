from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class MainForm(FlaskForm):
    make_test = SubmitField('Создать тест')
    take_test = SubmitField('Пройти тест')
    check_profile = SubmitField('Личный кабинет')


class MakingTestForm(FlaskForm):
    dropdown_list = ['Фильмы', 'Спорт', 'Еда', 'Игры', 'Музыка', 'Наука', 'Технологии', 'Другое']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Категория', choices=dropdown_list, default=1)
    describe = TextAreaField('Описание')
    photo = FileField('Фото', validators=[DataRequired()])
    add_question = SubmitField('+ Добавить вопрос +')


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
    photo = FileField('Фото (600x600)')
    question = StringField('Текст вопроса')
    add_question = SubmitField('+ Добавить вопрос +')
    answer1 = StringField('Ответ')
    check_right1 = BooleanField('Верный ответ')
    answer2 = StringField('Ответ')
    check_right2 = BooleanField('Верный ответ')
    answer3 = StringField('Ответ')
    check_right3 = BooleanField('Верный ответ')
    answer4 = StringField('Ответ')
    check_right4 = BooleanField('Верный ответ')
    create = SubmitField('Создать')


class ProfileView(FlaskForm):
    checked_tests = SubmitField('Пройденные тесты')
    created_tests = SubmitField('Созданные тесты')