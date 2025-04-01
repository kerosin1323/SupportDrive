from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class CreatingArticleDataForm(FlaskForm):
    categories = ['', 'Топ', 'Обзоры', 'Сравнения']
    brand = ['', 'Toyota', 'Volkswagen', 'Ford', 'Honda', 'Chevrolet', 'Nissan', 'Hyundai', 'BMW', 'Mercedes-Benz', 'Audi', 'Lada', 'УАЗ', 'Kia', 'Land Rover', 'Lexus', 'LiXiang', 'Mitsubishi', 'Porshe', 'Renault', 'Skoda', 'Subaru', 'Volvo', 'Exeed', 'Mazda', 'Changan', 'Chery', 'Citroen', 'GAC', 'Geely', 'Haval', 'Hyndai', 'Opel']
    body = ['', 'Седан', 'Хэтчбек', 'Внедорожник', 'Универсал', 'Электро']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Тип статьи', choices=categories)
    body_category = SelectField('Кузов', choices=body)
    photo = FileField('Добавить обложку')
    describe = TextAreaField('Описание')
    create = SubmitField('Создать')


class EditArticleForm(CreatingArticleDataForm):
    pass