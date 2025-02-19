from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class CreatingArticleDataForm(FlaskForm):
    countries = ['', 'Топ', 'Обзоры', 'Сравнения']
    brand = ['', 'Toyota', 'Volkswagen', 'Ford', 'Honda', 'Chevrolet', 'Nissan', 'Hyundai', 'BMW', 'Mercedes-Benz', 'Audi', 'Lada', 'УАЗ', 'Kia', 'Land Rover', 'Lexus', 'LiXiang', 'Mitsubishi', 'Porshe', 'Renault', 'Skoda', 'Subaru', 'Volvo', 'Exeed', 'Mazda']
    body = ['', 'Седан', 'Хэтчбек', 'Внедорожник', 'Универсал', 'Купе', 'Пикап', 'Минивэн']
    motors = ['', 'Бензин', 'Дизель', 'Гибрид','Электро']
    price_from = StringField('Цена от')
    price_to = StringField('до')
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Тип статьи', choices=countries)
    brand_category = SelectField('Марка', choices=brand)
    body_category = SelectField('Кузов', choices=body)
    motors_category = SelectField('Двигатель', choices=motors)
    photo = FileField('Добавить обложку')
    describe = TextAreaField('Описание')
    create = SubmitField('Создать')
