from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class CreatingArticleDataForm(FlaskForm):
    building = ['Легковые', 'Грузовые', 'Электро']
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField('Строение', choices=building)
    key_words = StringField('Ключевые слова', validators=[DataRequired()])
    photo = FileField('Добавить обложку')
    back = SubmitField('Назад')
    describe = TextAreaField('Описание')
    create = SubmitField('Создать')


class CommentsArticle(FlaskForm):
    text = TextAreaField()



class Filter(FlaskForm):
    types = ['По времени', 'По просмотрам', 'По оценке']
    times = ['День', 'Месяц', 'Год']
    type = SelectField('Фильтр')
    time = SelectField('За последний')




