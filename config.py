import os
import psycopg2


def try_connect():
    conn = psycopg2.connect(dbname='ChickenAlert', user='postgres',
                            password='Qwerty7', host='localhost')
    # cursor = conn.cursor()
    return conn


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ricchipicchi'