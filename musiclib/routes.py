from flask import render_template, url_for, flash, redirect, request
from musiclib import app, conn, bcrypt, mysql
from musiclib.forms import RegisterForm, LoginForm, SearchForm, PlaylistForm
from musiclib.models import MyUser
from flask_login import login_user, current_user, logout_user, login_required
from datetime import date

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
        cur.close()
        if temp != None:
            user = MyUser(temp[0], temp[1], temp[2], temp[3])
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
    username = current_user.get_user()
    cur = conn.cursor()
    cur.execute("SELECT * FROM PublicPlaylist WHERE userid=%s", current_user.get_id())
    public=cur.fetchall()
    cur.execute("SELECT * FROM PrivatePlaylist WHERE userid=%s", current_user.get_id())
    private=cur.fetchall()
    cur.close()
    return render_template('account.html', title='Account', username=username, public=public, private=private)

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
                cur.execute("SELECT * FROM User WHERE id <> %s", current_user.get_id())
                results = cur.fetchall()
            else:
                flash('Invalid table selection')
                cur.close()
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
                cur.close()
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
        return render_template('songs.html', results=results, songID=songID)
    else:
        flash("This song wasn't found in our database.", 'info')
        return redirect(url_for('Search'))
    return render_template('songs.html', title='Song')

@app.route('/user')
@login_required
def UserPage():
    userID= request.args.get('userID')
    results=()
    cur = conn.cursor()
    cur.execute("SELECT username FROM User where id = %s", userID)
    username=cur.fetchone()
    cur.execute("SELECT * FROM PublicPlaylist WHERE userid=%s", userID)
    results = cur.fetchall()
    cur.close()
    return render_template('publicaccount.html', title='User', username=username[0], results=results)

@app.route('/view')
@login_required
def ViewPlaylist():
    candelete= request.args.get('candelete')
    playlistID=request.args.get('playlistID')
    name=request.args.get('name')
    cur = conn.cursor()
    cur.execute("SELECT PublicSongs.songid, Song.title, Artist.name, Album.title FROM PublicSongs, Song, Artist, Album WHERE PublicSongs.playlistID = %s AND PublicSongs.songid = Song.id AND Artist.id = Song.artistID AND Album.id = Song.albumID", playlistID)
    results = cur.fetchall()
    cur.close()
    return render_template('playlist.html', title='View', candelete=candelete, name=name, results=results, playlistid=playlistID, playlistType='public')

@app.route('/privateview')
@login_required
def ViewPrivate():
    candelete= request.args.get('candelete')
    playlistID=request.args.get('playlistID')
    name=request.args.get('name')
    cur = conn.cursor()
    cur.execute("SELECT * FROM PrivateSongs WHERE playlistID = %s", playlistID)
    results = cur.fetchall()
    cur.execute("SELECT PrivateSongs.songid, Song.title, Artist.name, Album.title FROM PrivateSongs, Song, Artist, Album WHERE PrivateSongs.playlistID = %s AND PrivateSongs.songid = Song.id AND Artist.id = Song.artistID AND Album.id = Song.albumID", playlistID)
    results = cur.fetchall()
    cur.close()
    return render_template('playlist.html', title='Private View', candelete=candelete, name=name, results=results, playlistid=playlistID, playlistType='private')

@app.route('/public', methods=['GET', 'POST'])
@login_required
def PublicPlaylist():
    songID= request.args.get('songID')
    form = PlaylistForm()
    if form.validate_on_submit():
        userid = current_user.get_id()
        cur=conn.cursor()
        cur.execute("SELECT id FROM PublicPlaylist WHERE name = %s", form.playlistName.data)
        results = cur.fetchall()
        if(len(results) > 0):
            flash("Playlist with that name already exists")
            return redirect(url_for('Search'))
        cur.execute("INSERT INTO PublicPlaylist(name, datecreated, userid, id) VALUES(%s, %s, %s, NULL)", (form.playlistName.data, date.today(), userid))
        conn.commit()
        cur.execute("INSERT INTO PublicSongs(id, userid, songid, playlistID) VALUES(NULL, %s, %s, LAST_INSERT_ID())", (userid, songID))
        conn.commit()
        cur.close()
        return redirect(url_for('Search'))
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT name FROM PublicPlaylist where userid=%s", (current_user.get_id()))
    results = cur.fetchall()
    cur.close()
    reqtype = 'Public'
    return render_template('user.html', form=form, title='User', results=results, songID=songID, reqtype=reqtype)

@app.route('/deletesong', methods=['GET', 'POST'])
@login_required
def DeleteSong():
    candelete=request.args.get('candelete')
    songID= request.args.get('songID')
    playlistID= request.args.get('playlistid')
    playlistType= request.args.get('playlistType')
    name=request.args.get('name')
    if playlistType == 'public':
        cur=conn.cursor()
        cur.execute("delete from PublicSongs where playlistID=%s and songid=%s", (playlistID, songID))
        conn.commit()
        cur.execute("SELECT PublicSongs.songid, Song.title, Artist.name, Album.title FROM PublicSongs, Song, Artist, Album WHERE PublicSongs.playlistID = %s AND PublicSongs.songid = Song.id AND Artist.id = Song.artistID AND Album.id = Song.albumID", playlistID)
        results = cur.fetchall()
        print(len(results))
        if not results:
            cur.execute("delete from PublicPlaylist where id=%s ", playlistID)
            conn.commit()
            cur.close()
            return redirect(url_for('Account'))
        cur.close()
        return render_template('playlist.html', title='View', candelete=candelete, name=name, results=results, playlistid=playlistID, playlistType='public')
    elif playlistType == 'private':
        cur=conn.cursor()
        cur.execute("delete from PrivateSongs where playlistID=%s and songid=%s", (playlistID, songID))
        conn.commit()
        cur.execute("SELECT PrivateSongs.songid, Song.title, Artist.name, Album.title FROM PrivateSongs, Song, Artist, Album WHERE PrivateSongs.playlistID = %s AND PrivateSongs.songid = Song.id AND Artist.id = Song.artistID AND Album.id = Song.albumID", playlistID)
        results = cur.fetchall()
        if not results:
            cur.execute("delete from PrivatePlaylist where id=%s ", playlistID)
            conn.commit()
            cur.close()
            return redirect(url_for('Account'))
        cur.close()
        return render_template('playlist.html', title='View', candelete=candelete, name=name, results=results, playlistid=playlistID, playlistType='private')
    else:
        flash(f"Failed to delete your song from { name }. Try again.", 'info')
        return redirect(url_for('Account'))


@app.route('/private', methods=['GET', 'POST'])
@login_required
def PrivatePlaylist():
    songID= request.args.get('songID')
    form = PlaylistForm()
    if form.validate_on_submit():
        userid = current_user.get_id()
        cur=conn.cursor()
        cur.execute("SELECT id FROM PrivatePlaylist WHERE name = %s", form.playlistName.data)
        results = cur.fetchall()
        if(len(results) > 0):
            flash("Playlist with that name already exists")
            return redirect(url_for('Search'))
        cur.execute("INSERT INTO PrivatePlaylist(name, datecreated, userid, id) VALUES(%s, %s, %s, NULL)", (form.playlistName.data, date.today(), userid))
        conn.commit()
        cur.execute("INSERT INTO PrivateSongs(id, userid, songid, playlistID) VALUES(NULL, %s, %s, LAST_INSERT_ID())", (userid, songID))
        conn.commit()
        cur.close()
        return redirect(url_for('Search'))
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT name FROM PrivatePlaylist where userid=%s", (current_user.get_id()))
    results = cur.fetchall()
    cur.close()
    reqtype = 'Private'
    return render_template('user.html', form=form, title='User', results=results, songID=songID, reqtype=reqtype)

@app.route('/addpublic')
@login_required
def AddPublicSong():
    playlist = request.args.get('playlist')
    userid = current_user.get_id()
    songID = request.args.get('songID')
    cur=conn.cursor()
    cur.execute("SELECT id FROM PublicPlaylist WHERE name = %s", playlist)
    results = cur.fetchall()
    cur.execute("SELECT songid FROM PublicSongs WHERE songid = %s", songID)
    check = cur.fetchone()
    if check != None:
        flash(f"The song you've selected is already in { playlist }", 'info')
        cur.close()
        return redirect(url_for('Search'))
    else:
        cur.execute("INSERT INTO PublicSongs(id, userid, songid, playlistID) VALUES(NULL, %s, %s, %s)", (userid, songID, results[0]))
        conn.commit()
        cur.close()
        return redirect(url_for('Search'))

@app.route('/addprivate')
@login_required
def AddPrivateSong():
    playlist = request.args.get('playlist')
    userid = current_user.get_id()
    songID = request.args.get('songID')
    cur=conn.cursor()
    cur.execute("SELECT id FROM PrivatePlaylist WHERE name = %s", playlist)
    results = cur.fetchone()
    cur.execute("SELECT songid FROM PrivateSongs WHERE songid = %s", songID)
    check = cur.fetchone()
    if check != None:
        cur.close()
        flash(f"The song you've selected is already in { playlist }", 'info')
        return redirect(url_for('Search'))
    else:
        cur.execute("INSERT INTO PrivateSongs(id, userid, songid, playlistID) VALUES(NULL, %s, %s, %s)", (userid, songID, results[0]))
        conn.commit()
        cur.close()
        return redirect(url_for('Search'))

@app.route('/logout')
def Logout():
    logout_user()
    return redirect(url_for('Login'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404')