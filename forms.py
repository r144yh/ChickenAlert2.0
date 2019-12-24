from flask_wtf import FlaskForm
from psycopg2._psycopg import cursor
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, DateField
from wtforms.validators import DataRequired, Email, ValidationError
from config import try_connect


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    ppassword = PasswordField('Пароль', validators=[DataRequired()])
    reg_date = DateField('Дата Регистрации')
    target_weight = DecimalField('Целевой вес')
    current_weight = DecimalField('Текущий вес')
    calories = DecimalField('Кол-во каллорий в день')
    height = DecimalField('Рост')
    age = DecimalField('Возраст')
    gender = StringField('Пол')
    submit = SubmitField('Регистрация')
    #
    # def validate_login(self, login):
    #     login = login.data
    #     conn = try_connect()
    #     records = cursor.execute('SELECT login FROM uuser WHERE login = %s', (login, ))
    #     if records:
    #         raise ValidationError('Choose another login')


