from flask import Flask, request
from flask_bcrypt import Bcrypt
from flaskext.mysql import MySQL
from flask_login import LoginManager
import secrets
import os

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

mysql = MySQL()


app.config['MYSQL_DATABASE_HOST'] = 'localhost'
print("Enter username:")
app.config['MYSQL_DATABASE_USER'] = input()
print("Enter password:")
app.config['MYSQL_DATABASE_PASSWORD'] = input()
app.config['MYSQL_DATABASE_DB'] = 'jts0270'
mysql.init_app(app)

bcrypt = Bcrypt(app)
conn = mysql.connect()
loginManager = LoginManager()
loginManager.login_view = 'Login'   
loginManager.login_message_category = 'info'
loginManager.init_app(app)


from musiclib import routes



'''



@app.route('/', methods=['GET', 'POST'])
def index():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Artist")
    data = []
    for item in cur:
        data.append(item)
        print(item)
    conn.close()
    return str(data)














'''
