from flask import Flask, request
from flaskext.mysql import MySQL
app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
print("Enter user:")
app.config['MYSQL_DATABASE_USER'] = input()
print("Enter pass:")
app.config['MYSQL_DATABASE_PASSWORD'] = input()
app.config['MYSQL_DATABASE_DB'] = 'jts0270'
mysql.init_app(app)

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

if __name__ == '__main__':
    app.run(host='10.144.192.158', port = 8080)
