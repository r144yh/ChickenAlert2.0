from flask import Flask, request, jsonify
from flask import render_template, flash, redirect, url_for, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from config import Config, try_connect
from forms import LoginForm, RegistrationForm
from flask_bootstrap import Bootstrap
import psycopg2
import json
from contextlib import closing
from models import User
from flask_moment import Moment
import datetime

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
    major = True
    return render_template('index.html', title='Home', major=major)


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
        cursor.execute('INSERT INTO uuser VALUES(DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )',
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


@app.route('/profile/<uuser_id>')
@login_required
def profile(uuser_id):
    conn = try_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT uuser_id, login, email, reg_date, target_weight, current_weight, calories, '
                   'height, age, gender '
                   'FROM uuser '
                   'WHERE uuser_id = %s',
                   (uuser_id, ))
    records = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile.html', title='Profile', records=records)


@app.route('/nutrition_program/<nutrition_id>')
def nutrition_program(nutrition_id):
    conn = try_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * '
                   'FROM nutritionprogram NATURAL JOIN sportprogram '
                   'WHERE nutrition_id = %s',
                   (nutrition_id, ))
    records = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('nutrition_program.html', title='Nutrition Program', records=records)


@app.route('/sport_program/<sport_id>')
def sport_program(sport_id):
    conn = try_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * '
                   'FROM sportprogram NATURAL JOIN placetrena '
                   'WHERE sport_id = %s',
                   (sport_id,))
    records = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('sport_program.html', title='Sport Program', records=records)


@app.route('/test/<test_id>', methods=["GET", "POST"])
def test(test_id):
    conn = try_connect()
    cursor = conn.cursor()
    list1 = []
    # cursor.execute('SELECT count(distinct que_id) FROM question WHERE test_id = %s', (test_id, ))
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

    # cursor.execute('SELECT * FROM test NATURAL JOIN question NATURAL JOIN answer WHERE test_id = %s', (test_id,))
    # test = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('Test.html', title='Your Test', len_ans=list1)


if __name__ == '__main__':
    app.run(debug=True)
