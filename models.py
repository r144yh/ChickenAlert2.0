from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin):
    def __init__(self, id):
        self.id = id
        # self.res = self.getRes()

    # def getRes(self):
    #     temp = 0
    #     return temp

    def __repr__(self):
        return "%d" % self.id
