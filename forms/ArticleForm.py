from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class CreatingArticleForm(FlaskForm):
    name = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Текст')
    add_format = SubmitField('+')
    save = SubmitField('Далее')


class CreatingArticleDataForm(FlaskForm):
    categories_list = ['Фильмы', 'Спорт', 'Еда', 'Игры', 'Музыка', 'Наука', 'Технологии', 'Другое']
    category = SelectField('Категория', choices=categories_list)
    key_words = StringField('Ключевые слова')
    photo = FileField('Добавить обложку')
    back = SubmitField('Назад')
    create = SubmitField('Создать')


class ArticleMenu(FlaskForm):
    add_header = SubmitField('Заголовок')
    add_quote = SubmitField('Цитата')
    add_marking_list = SubmitField('Список')
    add_numeral_list = SubmitField('Нумерованный список')
    add_picture = SubmitField('Изображение')


class TextRedactor(FlaskForm):
    to_bold = SubmitField('Ж')
    to_cursive = SubmitField('К')
    add_link = SubmitField('Ссылка')
    to_underline = SubmitField('П')
    to_cross_out = SubmitField('З')


class ChangingArticleForm(FlaskForm):
    dropdown_list = ['Фильмы', 'Спорт', 'Еда', 'Игры', 'Музыка', 'Наука', 'Технологии', 'Другое']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Категория', choices=dropdown_list, default=1)
    describe = TextAreaField('Описание')
    add_photo = FileField('Добавить фото', validators=[DataRequired()])
    add_question = SubmitField('+ Изменить вопрос +')


