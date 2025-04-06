from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField


class CreatingQuestionForm(FlaskForm):
    brand = ['', 'Toyota', 'Volkswagen', 'Ford', 'Honda', 'Chevrolet', 'Nissan', 'Hyundai', 'BMW', 'Mercedes-Benz',
             'Audi', 'Lada', 'УАЗ', 'Kia', 'Land Rover', 'Lexus', 'LiXiang', 'Mitsubishi', 'Porshe', 'Renault', 'Skoda',
             'Subaru', 'Volvo', 'Exeed', 'Mazda', 'Changan', 'Chery', 'Citroen', 'GAC', 'Geely', 'Haval', 'Hyndai',
             'Opel']
    body = ['', 'Седан', 'Хэтчбек', 'Внедорожник', 'Универсал', 'Электро']
    name = StringField('Название')
    body_category = SelectField('Кузов', choices=body)
    create = SubmitField('Создать')


class EditQuestionForm(CreatingQuestionForm):
    pass