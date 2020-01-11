from flask_wtf import FlaskForm
from psycopg2._psycopg import cursor
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, DateField, RadioField, \
    IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError, NumberRange
from config import try_connect


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

    def validate_username(self, login):
        user = login.data
        conn = try_connect()
        cursor1 = conn.cursor()
        cursor1.execute('SELECT login FROM uuser WHERE login = %s', (user,))
        records = cursor1.fetchone()
        if not records:
            raise ValidationError('No such username')
        cursor1.close()
        conn.close()

    def validate_password(self, password):
        pas = password.data
        user = self.login.data
        conn = try_connect()
        cursor1 = conn.cursor()
        cursor1.execute('SELECT ppassword FROM uuser WHERE login = %s and ppassword = %s', (user,pas))
        records = cursor1.fetchone()
        if not records:
            raise ValidationError('Wrong password')
        cursor1.close()
        conn.close()


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


class EditProfileForm(FlaskForm):
    target_weight = DecimalField('Целевой вес', validators=[NumberRange(min=40, max=300)])
    current_weight = DecimalField('Текущий вес', validators=[NumberRange(min=20, max=300)])
    calories = DecimalField('Кол-во каллорий в день', validators=[NumberRange(min=0, max=10000)])
    height = DecimalField('Рост', validators=[NumberRange(min=0, max=300)])
    age = DecimalField('Возраст', validators=[NumberRange(min=0, max=100)])
    submit = SubmitField('Submit')


class FeedbackForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()])
    head = StringField('Your lost kilos', validators=[DataRequired()])
    text = TextAreaField('Your Feedback', validators=[DataRequired()])
    submit = SubmitField('Submit')


