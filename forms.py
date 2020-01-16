from flask_wtf import FlaskForm
from psycopg2._psycopg import cursor
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, DateField, RadioField, \
    IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError, NumberRange, InputRequired
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


class TestForm(FlaskForm):
    result = RadioField('Ответ', choices=[('', '')])


class TestForm(FlaskForm):
    conn = try_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT que_text FROM question ORDER BY que_id ASC ')
    que = cursor.fetchall()
    cursor.execute('SELECT answer_score, answer_text FROM answer  WHERE que_id = 1')
    ans = cursor.fetchall()
    result1 = RadioField(label=que[0][0], coerce=int, choices=ans, validators=[InputRequired()])
    cursor.execute('SELECT answer_score, answer_text FROM answer  WHERE que_id = 2')
    ans = cursor.fetchall()
    result2 = RadioField(label=que[1][0], coerce=int, choices=ans, validators=[InputRequired()])
    cursor.execute('SELECT answer_score, answer_text FROM answer  WHERE que_id = 3')
    ans = cursor.fetchall()
    result3 = RadioField(label=que[2][0], coerce=int, choices=ans, validators=[InputRequired()])
    cursor.execute('SELECT answer_score, answer_text FROM answer  WHERE que_id = 4')
    ans = cursor.fetchall()
    result4 = RadioField(label=que[3][0], coerce=int, choices=ans, validators=[InputRequired()])
    cursor.execute('SELECT answer_score, answer_text FROM answer  WHERE que_id = 5')
    ans = cursor.fetchall()
    result5 = RadioField(label=que[4][0], coerce=int, choices=ans, validators=[InputRequired()])
    cursor.execute('SELECT answer_score, answer_text FROM answer  WHERE que_id = 6')
    ans = cursor.fetchall()
    result6 = RadioField(label=que[5][0], coerce=int, choices=ans, validators=[InputRequired()])
    cursor.execute('SELECT answer_score, answer_text FROM answer  WHERE que_id = 7')
    ans = cursor.fetchall()
    result7 = RadioField(label=que[6][0], coerce=int, choices=ans, validators=[InputRequired()])
    cursor.execute('SELECT answer_score, answer_text FROM answer  WHERE que_id = 8')
    ans = cursor.fetchall()
    result8 = RadioField(label=que[7][0], coerce=int, choices=ans, validators=[InputRequired()])
    cursor.close()
    conn.close()
    submit = SubmitField('Submit')
