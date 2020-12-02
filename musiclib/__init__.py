from flask import Flask, request
from flask_bcrypt import Bcrypt
from flaskext.mysql import MySQL
import secrets

app = Flask(__name__)

mysql = MySQL()


app.config['MYSQL_DATABASE_HOST'] = 'local'
print("Enter username:")
app.config['MYSQL_DATABASE_USER'] = input()
print("Enter password:")
app.config['MYSQL_DATABASE_DB'] = 'jts0270'
mysql.init_app(app)

bcrypt = Bcrypt(app)
conn = mysql.connect()




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