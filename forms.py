from flask_wtf import FlaskForm
from psycopg2._psycopg import cursor
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, DateField, RadioField, IntegerField
from wtforms.validators import DataRequired, Email, ValidationError, NumberRange
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
    # reg_date = DateField('Дата Регистрации')
    target_weight = DecimalField('Целевой вес', validators=[NumberRange(min=40, max=300)])
    current_weight = DecimalField('Текущий вес', validators=[NumberRange(min=20, max=300)])
    calories = DecimalField('Кол-во каллорий в день', validators=[NumberRange(min=0, max=10000)])
    height = DecimalField('Рост', validators=[NumberRange(min=0, max=300)])
    age = DecimalField('Возраст', validators=[NumberRange(min=0, max=100)])
    # gender = StringField('Пол')
    gender = RadioField('Пол', choices=[('Female', 'Female'), ('Male', 'Male')])
    submit = SubmitField('Register')
    #
    # def validate_login(self, login):
    #     login = login.data
    #     conn = try_connect()
    #     records = cursor.execute('SELECT login FROM uuser WHERE login = %s', (login, ))
    #     if records:
    #         raise ValidationError('Choose another login')


class EditProfileForm(FlaskForm):
    target_weight = DecimalField('Целевой вес', validators=[NumberRange(min=40, max=300)])
    current_weight = DecimalField('Текущий вес', validators=[NumberRange(min=20, max=300)])
    calories = DecimalField('Кол-во каллорий в день', validators=[NumberRange(min=0, max=10000)])
    height = DecimalField('Рост', validators=[NumberRange(min=0, max=300)])
    age = DecimalField('Возраст', validators=[NumberRange(min=0, max=100)])
    submit = SubmitField('Submit')


