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
                return redirect(url_for('Search'))
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
@login_required
def Search():
    search = SearchForm(request.form)
    if request.method == 'POST':
        return Results(search)
    return render_template('search.html', title='Search', form=search)

@app.route('/results')
@login_required
def Results(search):
    results = []
    searchStr = search.data['search']
    print(search.data)
    if(search.select.data != None):
        table = search.select.data
        cur = conn.cursor()
        # if multiple things are selected
        if search.data['search'] == '': 
            if(table == 'Artist'):
                cur.execute("SELECT * FROM Artist")
                results = cur.fetchall()
            elif(table == 'Album'):
                cur.execute("SELECT * FROM Album")
                results = cur.fetchall()
            elif(table == 'Songs'):
                cur.execute("SELECT * FROM Song")
                results = cur.fetchall()
            elif(table == 'User'):
                cur.execute("SELECT * FROM User")
                results = cur.fetchall()
            else:
                flash('Invalid table selection')
                return redirect(url_for('Search'))
         # if one thing is selected
        else:
            if(table == 'Artist'):
                cur.execute("SELECT * FROM Artist WHERE name = %s or genre = %s", (search.data['search'], search.data['search']))
                results = cur.fetchall()
            elif(table == 'Album'):
                cur.execute("SELECT * FROM Album WHERE title = %s or genre = %s", (search.data['search'], search.data['search']))
                results = cur.fetchall()
            elif(table == 'Songs'):
                cur.execute("SELECT * FROM Song WHERE title = %s or genre = %s", (search.data['search'], search.data['search']))
                results = cur.fetchall()
            elif(table == 'User'):
                cur.execute("SELECT * FROM User WHERE username = %s or email = %s", (search.data['search'], search.data['search']))
                results = cur.fetchall()
            else:
                flash('Invalid table selection')
                return redirect(url_for('Search'))
        cur.close()
    else:
        flash('Table not selected', 'info')
        return redirect(url_for('Search'))
    if not results:
        flash('Results not found', 'info')
        return redirect(url_for('Search'))
    else:
        # for result in results:
        #     for i in result:
        #         print(i)
        return render_template('results.html', title='Results', results=results, table=table)


@app.route('/artist')
@login_required
def Artist():
    artistID= request.args.get('artistID')
    cur = conn.cursor()
    cur.execute("SELECT name, genre FROM Artist WHERE id = %s", (artistID))
    artist = cur.fetchone()
    cur.execute("SELECT * FROM Album WHERE artistID = %s", (artistID))
    results = cur.fetchall()
    cur.close()
    if results != None:
        return render_template('artist.html', title='Artist', results=results, artistname=artist[0], genre=artist[1])
    else:
        flash("Artist has no albums in our database.")
        return redirect(url_for('Search'))

@app.route('/album')
@login_required
def Album():
    albumID= request.args.get('albumID')
    cur = conn.cursor()
    cur.execute("SELECT artistID, title FROM Album WHERE id = %s", (albumID))
    artist = cur.fetchone()
    cur.execute("SELECT name FROM Artist WHERE id = %s", (artist[0]))
    artistname = cur.fetchone()
    cur.execute("SELECT * FROM Song WHERE albumID = %s", (albumID))
    results = cur.fetchall()
    print(results)
    cur.close()
    if results != None:
        return render_template('album.html', artistname=artistname[0], title=artist[1], results=results, genre=results[0][2])
    else:
        flash("Album has no songs in our database.", 'info')
        return redirect(url_for('Search'))
    return render_template('album.html', title='Album')

@app.route('/songs')
@login_required
def Song():
    songID= request.args.get('songID')
    cur = conn.cursor()
    cur.execute("SELECT Song.title, Song.genre, Song.length, Album.title, Artist.name FROM Song, Album, Artist WHERE Song.artistID = Artist.id AND Song.albumID = Album.id AND Song.id = %s", (songID))
    results = cur.fetchone()
    print(results)

    cur.close()
#  artistname=results[4], title=results[0], genre=results[1], length=results[2], albumtitle=results[3], 
    if results != None:
        return render_template('songs.html', results=results)
    else:
        flash("This song wasn't found in our database.", 'info')
        return redirect(url_for('Search'))
    return render_template('songs.html', title='Song')

@app.route('/user')
@login_required
def UserPage():
    userID= request.args.get('userID')

    return render_template('user.html', title='User')

@app.route('/public')
@login_required
def PublicPlaylist():
        userID= request.args.get('userID')

    return render_template('user.html', title='User')

@app.route('/private')
@login_required
def PrivatePlaylist():
    userID= request.args.get('userID')

    return render_template('user.html', title='User')

@app.route('/logout')
def Logout():
    logout_user()
    return redirect(url_for('Login'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404')