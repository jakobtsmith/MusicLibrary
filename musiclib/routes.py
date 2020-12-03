from flask import render_template, url_for, flash, redirect, request
from musiclib import app, conn, bcrypt, mysql
from musiclib.forms import RegisterForm, LoginForm, SearchForm
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
    search = SearchForm(request.form)
    if request.method == 'POST':
        return Results(search)
    return render_template('search.html', title='Search', form=search)

@app.route('/results')
def Results(search):
    results = []
    searchStr = search.data['search']
    print(search.data)
    if(search.select.data != None):
        table = search.select.data
        cur = conn.cursor()
        if search.data['search'] == '':
            if(table == 'Artist'):
                cur.execute("SELECT name FROM Artist")
                results = cur.fetchall()
                for result in results:
                    print(result)
            elif(table == 'Album'):
                cur.execute("SELECT name FROM Album")
                results = cur.fetchall()
                for result in results:
                    print(result)
            elif(table == 'Song'):
                cur.execute("SELECT name FROM Song")
                results = cur.fetchall()
                for result in results:
                    print(result)
            elif(table == 'User'):
                cur.execute("SELECT name FROM User")
                results = cur.fetchall()
                for result in results:
                    print(result)
            else:
                flash('Invalid table selection')
                return redirect(url_for('Search'))
        else:
            if(table == 'Artist'):
                cur.execute("SELECT name FROM Artist WHERE name = %s or genre = %s", (search.data['search'], search.data['search']))
                results = cur.fetchall()
                for result in results:
                    print(result)
            elif(table == 'Album'):
                cur.execute("SELECT title FROM Album WHERE title = %s or genre = %s", (search.data['search'], search.data['search']))
                results = cur.fetchall()
                for result in results:
                    print(result)
            elif(table == 'Song'):
                cur.execute("SELECT title FROM Song WHERE title = %s or genre = %s", (search.data['search'], search.data['search']))
                results = cur.fetchall()
                for result in results:
                    print(result)
            elif(table == 'User'):
                cur.execute("SELECT username FROM User WHERE username = %s or email = %s", (search.data['search'], search.data['search']))
                results = cur.fetchall()
                for result in results:
                    print(result)
            else:
                flash('Invalid table selection')
                return redirect(url_for('Search'))
        cur.close()
    else:
        flash('No table selected')
        return redirect(url_for('Search'))
    if not results:
        flash('No search results')
        return redirect(url_for('Search'))
    else:
        print(results)
        return render_template('results.html', title='Results', results=results)


@app.route('/logout')
def Logout():
    logout_user()
    return redirect(url_for('Login'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404')