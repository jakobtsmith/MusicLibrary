from flask_login import UserMixin
from musiclib import loginManager

@loginManager.user_loader
def load_user(ID):
    return User



class User(UserMixin):

    def __init__(self, ID, username, password, email, active=True):
        self.ID = ID
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return f"User('{self.ID}', '{self.username}', '{self.email} ')"

    def is_active(self):
        return self.active

    def get_id(self):
        return (self.ID)