
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import datetime

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select id, title,time, text, likes from entries order by id desc')
    entries = cur.fetchall()
    cur = db.execute('select comment_id, commenttext from commentonentries order by id desc')
    commentonentries = cur.fetchall()
    return render_template('show_entries.html', entries=entries, commentonentries=commentonentries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/comment', methods=['POST'])
def add_comment():
    db = get_db()
    db.execute('insert into commentonentries(commenttext, comment_id) values(?,?)',
                [request.form['commenttext'], request.form['commentid']])
    db.commit()
    flash('New comment was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/post/<int:entry_id>')
def redirecttopost(entry_id):
    db = get_db()
    cur = db.execute('select id, title,time, text, likes from entries order by id desc')
    entries = cur.fetchall()
    cur = db.execute('select comment_id, commenttext from commentonentries order by id desc')
    commentonentries = cur.fetchall()
    return render_template('post.html', entries = entries, commentonentries = commentonentries, entry_id=entry_id)
	

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/likes/<entryid>/<likes>', methods=['GET', 'POST']) 
def likes(entryid, likes):
    likes = int(likes) + 1
    db = get_db()
    db.execute("""update entries set likes = ? where id = ?""",
                (likes, entryid))
    db.commit()
    flash("Thanks for the like")
    return redirect(url_for('show_entries'))

@app.route('/dislikes/<entryid>/<likes>', methods=['GET', 'POST']) 
def dislikes(entryid, likes):
    if int(likes) > 0:
        likes = int(likes) - 1
    db = get_db()
    db.execute("""update entries set likes = ? where id = ?""",
                (likes, entryid))
    db.commit()
    flash("Sorry to see you not liking it")
    return redirect(url_for('show_entries'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
