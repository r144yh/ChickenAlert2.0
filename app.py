from flask import Flask
from flask import render_template, flash, redirect, url_for, session
from flask_login import LoginManager, current_user, login_user, logout_user
from config import Config
from forms import LoginForm
from flask_bootstrap import Bootstrap
import psycopg2
from contextlib import closing

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
# -*- coding: utf-8 -*-
login = LoginManager(app)
login.login_view = 'login'


def try_connect():
    conn = psycopg2.connect(dbname='ChickenAlert', user='postgres',
                            password='Qwerty7', host='localhost')
    cursor = conn.cursor()
    return cursor


@app.route('/')
def main():
    return "Welcome!"


# @app.route('/showSignUp')
# def showSignUp():
#     return render_template('sign.html')


@app.route('/index')
def index():
    user = {'username': 'Эльдар Рязанов'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        },
        {
            'author': {'username': 'Ипполит'},
            'body': 'Какая гадость эта ваша заливная рыба!!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session['logged_in']:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        cursor = try_connect()
        cursor.execute('SELECT login FROM player WHERE login = %s and ppassword = %s',
                       (form.username.data, form.password.data))
        records = cursor.fetchall()
        if not records:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # login_user(user, remember=form.remember_me.data)

        session['logged_in'] = True
        cursor.close()
        return redirect(url_for('index'))
    return render_template('sign.html', title='Sign In', form=form)


if __name__ == '__main__':
    app.run(debug=True)
