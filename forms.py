from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField

from wtforms.validators import Length


class addCar(FlaskForm):
    name = StringField('Название', validators=[Length(min=1, max=40)])
    price = IntegerField('Цена')
    descriptionCar = StringField('Описание', validators=[Length(min=2, max=1500)])
    brandCar = StringField('Бренд', validators=[Length(min=1, max=40)])
    image = StringField('Картинка', validators=[Length(min=4, max=40)])
    sub = SubmitField('Добавить')



class addBrand(FlaskForm):
    brand = StringField('Название', validators=[Length(min=1, max=40)])
    descriptionBrand = StringField('Описание', validators=[Length(min=4, max=150)])
    sub = SubmitField('Добавить')



class Authorization(FlaskForm):
    login = StringField('Логин', validators=[Length(min=4, max=20)])
    password = PasswordField('Пароль', validators=[Length(min=4, max=20)])
    sub = SubmitField('Войти')



class Registration(FlaskForm):
    login = StringField('Логин', validators=[Length(min=4, max=20)])
    password = PasswordField('Пароль', validators=[Length(min=4, max=20)])
    confirm_password = PasswordField('Повторите пароль', validators=[Length(min=4, max=20)])
    sub = SubmitField('Войти')