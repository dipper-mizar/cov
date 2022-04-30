from user import db as user_db
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username, password, location=None, queue_num=None, email=None, rank=None):
        self.username = username
        self.password = password
        self.location = location
        self.queue_num = queue_num
        self.email = email
        self.rank = rank

    def get_id(self):
        pass

    def verify(self):
        password = user_db.query_user_password_by_username(self.username)[0][0]
        if password != self.password:
            return "密码错误"
        return 'OK'

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_location(self):
        return self.location

    def get_queue_num(self):
        return self.queue_num

    def get_email(self):
        return self.email

    def get_rank(self):
        return self.rank

    def set_username(self, username):
        self.username = username

    def set_password(self, password):
        self.password = password

    def set_location(self, location):
        self.location = location

    def set_queue_num(self, queue_num):
        self.queue_num = queue_num

    def set_email(self, email):
        self.email = email

    def set_rank(self, rank):
        self.rank = rank