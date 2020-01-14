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
    flag_no_prog = False
    if records[10] == 'No prog                                 ':
        flag_no_prog = True
    if records[12] is not None:
        days = int(records[12])
    else:
        days = 0
    cursor.close()
    conn.close()
    return render_template('profile.html', title='Profile', records=records, rand_num=rand_num, flag_no_prog=flag_no_prog, days=days)


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
                   'feedback.nutrition_id = %s', (nutrition_id, ))
    fb = cursor.fetchall()
    np_desc = records[3].split('.')
    nutr_breakfast = records[5].split('.')
    nutr_dinner = records[6].split('.')
    nutr_supper = records[7].split('.')
    nutr_snack = records[8].split('.')
    cursor.close()
    conn.close()
    return render_template('nutrition_program.html', title='Nutrition Program', records=records, np_desc=np_desc,
                           nutr_breakfast=nutr_breakfast, nutr_dinner=nutr_dinner, nutr_supper=nutr_supper, nutr_snack=nutr_snack, fb=fb)


@app.route('/set_prog/<nutrition_id>')
@login_required
def set_prog(nutrition_id):
    now = datetime.datetime.now()
    conn = try_connect()
    cursor = conn.cursor()
    cursor.execute('UPDATE uuser SET nutrition_id = %s, nutrition_start = %s WHERE uuser_id = %s', (nutrition_id, now, current_user.id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('nutrition_program', nutrition_id=nutrition_id))


@app.route('/sport_program/<sport_id>')
def sport_program(sport_id):
    conn = try_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * '
                   'FROM sportprogram NATURAL JOIN placetrena '
                   'WHERE sport_id = %s',
                   (sport_id,))
    records = cursor.fetchone()
    sp_header = records[3].split('.')
    sp_myths_header = records[4].split('.')
    sp_myths = records[5].split('.')
    pl_name = records[4].split('.')
    pl_desc = records[5].split('.')
    cursor.close()
    conn.close()
    major2 = True
    return render_template('sport_program.html', title='Sport Program', records=records, sp_header=sp_header,
                           sp_myths_header=sp_myths_header, sp_myths=sp_myths, pl_name=pl_name, pl_desc=pl_desc,
                           major2=major2)


@app.route('/test/<test_id>', methods=["GET", "POST"])
def test(test_id):
    form = TestForm()
    conn = try_connect()
    cursor = conn.cursor()
    list1 = []
    cursor.execute('SELECT que_id, que_text FROM question WHERE test_id = %s', (test_id,))
    kek = cursor.fetchall()
    for row in kek:
        cursor.execute('SELECT answer_text, answer_score '
                       'FROM answer WHERE que_id = %s',
                       (row[0],))
        records = cursor.fetchall()
        list = []
        for ans in records:
            list.append(ans)
        list1.append([row[1], list, row[0]])

    cursor.close()
    conn.close()
    return render_template('Test.html', title='Your Test', len_ans=list1, form=form)


@app.route('/404')
def error_404():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)
