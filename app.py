from flask import Flask, request, jsonify
from flask import render_template, flash, redirect, url_for, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from config import Config, try_connect
from forms import LoginForm, RegistrationForm, EditProfileForm, FeedbackForm, TestForm
from flask_bootstrap import Bootstrap
import psycopg2
import json
from contextlib import closing
from models import User
from flask_moment import Moment
import datetime
import numpy as np
import random

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
moment = Moment(app)
# -*- coding: utf-8 -*-
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/')
@login_required
def main():
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))


@app.route('/index')
def index():
    conn = try_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT name, np_name, feedback_head, feedback_text, feedback.nutrition_id FROM feedback, '
                   'nutritionprogram WHERE feedback.nutrition_id = nutritionprogram.nutrition_id')
    records = cursor.fetchall()
    random.shuffle(records)
    cursor.close()
    conn.close()
    major = True
    return render_template('index.html', title='Home', major=major, records=records)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        conn = try_connect()
        cursor = conn.cursor()
        cursor.execute('SELECT uuser_id FROM uuser WHERE login = %s and ppassword = %s',
                       (form.login.data, form.password.data))
        records = cursor.fetchone()
        if not records:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(User(records[0]), remember=form.remember_me.data)

        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect('index')
    form = RegistrationForm()
    if form.validate_on_submit():
        now = datetime.datetime.now()
        conn = try_connect()
        cursor = conn.cursor()
        nutrition_id = 1
        cursor.execute('INSERT INTO uuser VALUES(DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)',
                       (form.login.data, form.email.data, form.ppassword.data, now, form.target_weight.data,
                        form.current_weight.data,
                        form.calories.data,
                        form.height.data,
                        form.age.data,
                        form.gender.data,
                        nutrition_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Welcome, Chicken')
        return redirect(url_for('index'))
    flash('Oops, something was wrong')
    return render_template('registration.html', title='Registration', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile/<uuser_id>', methods=['GET', 'POST'])
@login_required
def profile(uuser_id):
    if current_user.id != uuser_id:
        return redirect(url_for('error_404'))
    rand_num = np.random.randint(1, 9)
    now = datetime.datetime.now()
    conn = try_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT uuser_id, login, email, reg_date, target_weight, current_weight, calories, '
                   'height, age, gender, np_name, nutrition_id, date_part(\'day\', %s - nutrition_start) '
                   'FROM uuser NATURAL JOIN nutritionprogram '
                   'WHERE uuser_id = %s',
                   (now, uuser_id,))
    records = cursor.fetchone()
    # cursor.execute('SELECT date(test_date), ans_result FROM test_result WHERE uuser_id = %s '
    #                'GROUP BY uuser_id, date(test_date), ans_result '
    #                'ORDER BY max(test_date) DESC ',
    #                (current_user.id, ))

    cursor.execute('SELECT date(test_date), ans_result FROM test_result WHERE uuser_id = %s '
                   'ORDER BY test_date DESC ',
                   (current_user.id,))
    kek = cursor.fetchone()
    cursor.execute('SELECT count(uuser_id) FROM test_result WHERE uuser_id = %s GROUP BY uuser_id',
                   (current_user.id,))
    kek1 = cursor.fetchone()
    flag_no_prog = False
    if records[10] == 'No prog                                 ':
        flag_no_prog = True
    if records[12] is not None:
        days = int(records[12])
    else:
        days = 0
    cursor.close()
    conn.close()
    return render_template('profile.html', title='Profile', records=records, rand_num=rand_num,
                           flag_no_prog=flag_no_prog, days=days, kek=kek, kek1=kek1)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        conn = try_connect()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE uuser SET target_weight = %s, current_weight = %s, calories = %s, height = %s, age = %s WHERE '
            'uuser_id = %s',
            (form.target_weight.data, form.current_weight.data, form.calories.data, form.height.data, form.age.data,
             current_user.id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Your changes have been saved.')
        return redirect(url_for('profile', uuser_id=current_user.id))
    elif request.method == 'GET':
        conn = try_connect()
        cursor = conn.cursor()
        cursor.execute('SELECT target_weight, current_weight, calories, height, age '
                       'FROM uuser  '
                       'WHERE uuser_id = %s',
                       (current_user.id,))
        records = cursor.fetchone()
        form.target_weight.data = records[0]
        form.current_weight.data = records[1]
        form.calories.data = records[2]
        form.height.data = records[3]
        form.age.data = records[4]
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/add_feedback<nutrition_id>', methods=['GET', 'POST'])
@login_required
def add_feedback(nutrition_id):
    if int(nutrition_id) != int(current_user.np):
        return redirect(url_for('error_404'))
    form = FeedbackForm()
    if form.validate_on_submit():
        conn = try_connect()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO feedback values(DEFAULT, %s, %s, %s, %s, %s)',
                       (form.head.data, form.text.data, nutrition_id, current_user.id, form.name.data))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('feedback.html', form=form)


@app.route('/nutrition_program/<nutrition_id>')
def nutrition_program(nutrition_id):
    conn = try_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * '
                   'FROM nutritionprogram NATURAL JOIN sportprogram '
                   'WHERE nutrition_id = %s',
                   (nutrition_id,))
    records = cursor.fetchone()
    cursor.execute('SELECT name, np_name, feedback_head, feedback_text FROM feedback, nutritionprogram WHERE '
                   'feedback.nutrition_id = nutritionprogram.nutrition_id AND '
                   'feedback.nutrition_id = %s', (nutrition_id,))
    fb = cursor.fetchall()
    np_desc = records[3].split('.')
    nutr_breakfast = records[5].split('.')
    nutr_dinner = records[6].split('.')
    nutr_supper = records[7].split('.')
    nutr_snack = records[8].split('.')
    cursor.close()
    conn.close()
    return render_template('nutrition_program.html', title='Nutrition Program', records=records, np_desc=np_desc,
                           nutr_breakfast=nutr_breakfast, nutr_dinner=nutr_dinner, nutr_supper=nutr_supper,
                           nutr_snack=nutr_snack, fb=fb)


@app.route('/sport_program/<sport_id>')
def sport_program(sport_id):
    conn = try_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * '
                   'FROM sportprogram NATURAL JOIN placetrena NATURAL JOIN training_exercise '
                   'WHERE sport_id = %s',
                   (sport_id,))
    records = cursor.fetchone()
    sp_header = records[4].split('.')
    sp_myths_header = records[5].split('.')
    sp_myths = records[6].split('.')
    pl_name = records[7].split('.')
    pl_desc = records[8].split('.')
    train_name = records[9].split('.')
    train_desc = records[10].split('.')
    cursor.close()
    conn.close()
    major2 = True
    return render_template('sport_program.html', title='Sport Program', records=records, sp_header=sp_header,
                           sp_myths_header=sp_myths_header, sp_myths=sp_myths, pl_name=pl_name, pl_desc=pl_desc,
                           train_name=train_name, train_desc=train_desc, major2=major2)


@app.route('/test/<test_id>', methods=["GET", "POST"])
def test(test_id):
    form = TestForm()
    if form.validate_on_submit():
        conn1 = try_connect()
        cursor1 = conn1.cursor()
        test_result = int(form.result1.data) + int(form.result2.data) + int(form.result3.data) + int(
            form.result4.data) + int(
            form.result5.data) + int(form.result6.data) + int(form.result7.data) + int(form.result8.data)
        print(test_result)
        if test_result <= 10:
            test_result = 10
        elif 10 < test_result <= 20:
            test_result = 20
        elif 20 < test_result <= 30:
            test_result = 30
        elif 30 < test_result <= 40:
            test_result = 40
        elif 40 < test_result <= 50:
            test_result = 50
        elif 50 < test_result <= 60:
            test_result = 60
        else:
            test_result = 60
        now = datetime.datetime.now()
        cursor1.execute('UPDATE uuser SET nutrition_id = %s, nutrition_start = %s WHERE uuser_id = %s',
                        (test_result, now, current_user.id))
        conn1.commit()

        cursor1.execute('INSERT INTO test_result VALUES(DEFAULT, %s, %s, %s, %s)',
                        (current_user.id, test_id, test_result, now))
        conn1.commit()
        cursor1.close()
        conn1.close()
        return redirect(url_for('nutrition_program', nutrition_id=test_result))

    return render_template('Test.html', title='Your Test', form=form)


@app.route('/404')
def error_404():
    return render_template('error.html')


@app.route('/useful_information/<usefuli_id>', methods=["GET", "POST"])
def useful_information(usefuli_id):
    if current_user.is_anonymous:
        return redirect(url_for('error_404'))

    conn = try_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * '
                    'FROM usefulinformation '
                    'WHERE usefuli_id = %s',
                    (usefuli_id,))
    records = cursor.fetchone()
    us_list_head = records[3].split('.')
    us_list = records[4].split('.')
    us_ex_head = records[5].split('.')
    us_ex = records[6].split('.')
    cursor.close()
    conn.close()
    flag_pict1 = False
    if records[0] == 1:
        flag_pict1 = True
    flag_pict2 = False
    if records[0] == 2:
        flag_pict2 = True
    flag_pict3 = False
    if records[0] == 3:
        flag_pict3 = True
    major3 = True
    return render_template('us_information.html', title='Useful Information', records=records, major3=major3,
                           us_list_head=us_list_head, us_list=us_list, us_ex_head=us_ex_head, us_ex=us_ex,
                           flag_pict1=flag_pict1, flag_pict2=flag_pict2, flag_pict3=flag_pict3)


if __name__ == '__main__':
    app.run(debug=True)
