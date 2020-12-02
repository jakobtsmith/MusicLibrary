from flask import render_template, url_for, flash, redirect, request
from musiclib import app, conn, bcrypt
from musiclib.forms import RegisterForm, LoginForm

# homepage is the login page
@app.route('/', methods=['GET', 'POST'])
def Login():
    pass
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM Artist")
    # data = []
    # for item in cur:
    #     data.append(item)
    #     print(item)
    # conn.close()
    # return str(data)

two = 1*1
@app.route('/register', methods=['GET', 'POST'])
def Register():
    if current_user.is_authenticated:
        return redirect(url_for('Account'))
    form = RegisterForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        hashPass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        cur.execute("INSERT INTO User(username, password, email) VALUES(%s, %s, %s)", (form.username.data, hashPass, form.email.data))
        mysql.connection.commit()
        flash("Your account has been created!", 'success')
        return redirect(url_for('Login'))
    return render_template('register.html', title='Search', form=form)

@app.route('/account', methods=['GET', 'POST'])
def Account():
    return render_template('account.html', title='Search')

@app.route('/search', methods=['GET', 'POST'])
def Search():
    return render_template('search.html', title='Search')
