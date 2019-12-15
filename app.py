from flask import Flask, request
from flask import render_template, flash, redirect, url_for, session
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_manager, login_required
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm
from flask_bootstrap import Bootstrap
import psycopg2
from contextlib import closing

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
# -*- coding: utf-8 -*-
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def try_connect():
    conn = psycopg2.connect(dbname='ChickenAlert', user='postgres',
                            password='Qwerty7', host='localhost')
    cursor = conn.cursor()
    return cursor


@app.route('/')
def main():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))
#     return 'tet'


@app.route('/index')
def index():
    user = {'username': 'Гера Дук'}
    return render_template('index.html', title='Home', user=user)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if session['logged_in']:
#         return redirect(url_for('index'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         cursor = try_connect()
#         cursor.execute('SELECT login FROM uuser WHERE login = %s and ppassword = %s',
#                        (form.username.data, form.password.data))
#         records = cursor.fetchall()
#         if not records:
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
#         # login_user(user, remember=form.remember_me.data)
#
#         session['logged_in'] = True
#         cursor.close()
#         return redirect(url_for('index'))
#     return render_template('login.html', title='Sign In', form=form)

@login_manager.user_loader
def load_user(uuser_id):
    return uuser(uuser_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.metod == "POST":
        username = request.form["login"]
        password = request.form["password"]
        remember_me = request.form["remember"]
        user = get_user('SELECT login FROM uuser WHERE login = %s and ppassword = %s')
        if user:
            login_user(user, remember=remember_me)
            return redirect(url_for('index'))
        return render_template('login.html', title='Sign In')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(somwhere)
# @app.route('/logout')
# def logout():
#     session['logged_in'] = False
#     # logout_user()
#     return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
