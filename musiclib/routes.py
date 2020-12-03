from flask import render_template, url_for, flash, redirect, request
from musiclib import app, conn, bcrypt, mysql
from musiclib.forms import RegisterForm, LoginForm
from musiclib.models import User
from flask_login import login_user, current_user, logout_user, login_required

# homepage is the login page
@app.route('/', methods=['GET', 'POST'])
def Login():
    if current_user.is_authenticated:
       return redirect(url_for('Account'))
    form = LoginForm()
    if form.validate_on_submit():
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM User WHERE email = %s", (form.email.data))
        temp = cur.fetchone()
        if temp != None:
            user = User(temp[0], temp[1], temp[2], temp[3])
            if bcrypt.check_password_hash(user.password, form.password.data):
                flash('You\'ve logged in successfully!', 'success')
                login_user(user, remember=form.remember.data)
                return redirect(url_for('Account'))
            else:
                flash('Login Unsuccessful. Check email and password', 'danger')
        else:
            flash('Email doesn\'t exist. Please register before logging in.', 'danger')
    return render_template('login.html', title='Login', form=form)
    

@app.route('/register', methods=['GET', 'POST'])
def Register():
    if current_user.is_authenticated:
       return redirect(url_for('Account'))
    form = RegisterForm()
    if form.validate_on_submit():
        conn = mysql.connect()
        cur = conn.cursor()
        hashPass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        cur.execute("INSERT INTO User(username, password, email) VALUES(%s, %s, %s)", (form.username.data, hashPass, form.email.data))
        conn.commit()
        cur.close()
        conn.close()
        flash("Your account has been created!", 'success')
        return redirect(url_for('Login'))
    return render_template('register.html', title='Search', form=form)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def Account():
    return render_template('account.html', title='Search')

@app.route('/search', methods=['GET', 'POST'])
def Search():
    return render_template('search.html', title='Search')

@app.route('/logout')
def Logout():
    logout_user()
    return redirect(url_for('Login'))