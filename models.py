from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from config import try_connect


class User(UserMixin):
    def __init__(self, id):
        self.id = id
        # self.res = self.getRes()
        self.np = self.getNP()

    # def getRes(self):
    #     temp = 0
    #     return temp

    def getNP(self):
        conn = try_connect()
        cursor = conn.cursor()
        cursor.execute('SELECT nutrition_id FROM uuser WHERE uuser_id = %s', (self.id, ))
        np = cursor.fetchone()
        return np[0]

    def __repr__(self):
        return "%d" % self.id
