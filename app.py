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

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
moment = Moment(app)
# -*- coding: utf-8 -*-
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# cur = try_connect()
# cur.execute('SELECT * FROM database WHERE cheto = %s', (cheto, ))


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
    user = {'username': 'Гера Дук'}
    return render_template('index.html', title='Home', user=user)


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
        conn = try_connect()
        cursor = conn.cursor()
        nutrition_id = 1
        cursor.execute('INSERT INTO uuser VALUES(DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )',
                     (form.login.data, form.email.data, form.ppassword.data, form.reg_date.data, form.target_weight.data,
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

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.metod == "POST":
#         cur = try_connect()
#
#         username = request.form["login"]
#         password = request.form["password"]
#         remember_me = request.form["remember"]
#         user = cur.execute('SELECT uuser_id FROM uuser WHERE login = %s and ppassword = %s',
#                            (username, password))
#         if user:
#             login_user(user, remember=remember_me)
#             return redirect(url_for('index'))
#         return render_template('login.html', title='Sign In')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
