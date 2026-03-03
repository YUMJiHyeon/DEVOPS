# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import re
import time
import sqlite3
from hashlib import md5
from datetime import datetime
from contextlib import closing
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


# configuration
DATABASE = '/tmp/minitwit.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://68.183.13.121:27017/minitwit"
app.config["SECRET_KEY"] = 'development key'
app.config["DEBUG"] = True

mongo = PyMongo(app)


def query_db(collection, query=None, one=False, limit=None):
    if query is None:
        query = {}
    cursor = mongo.db[collection].find(query).sort('_id',-1)
    if limit:
        cursor = cursor.limit(limit)
    rv = list(cursor)
    for item in rv:
        item['user_id'] = str(item.get('_id'))
    return (rv[0] if rv else None) if one else rv

def format_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

def gravatar_url(email, size=80):
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = mongo.db.user.find_one({"_id": ObjectId(session['user_id'])})



@app.route('/')
def timeline():
    if not g.user:
        return redirect(url_for('public_timeline'))
    messages = query_db('message', limit=PER_PAGE)
    return render_template('timeline.html', messages=messages)

@app.route('/public')
def public_timeline():
    messages = query_db('message', limit=PER_PAGE)
    return render_template('timeline.html', messages=messages)    

@app.route('/<username>')
def user_timeline(username):
    profile_user = mongo.db.user.find_one({"username": username})
    if profile_user is None:
        abort(404)
    profile_user['user_id'] = str(profile_user['_id'])
    messages = query_db('message', {'author_id': str(profile_user['_id'])}, limit=PER_PAGE)
    
    followed = False
    if g.user:
        record = mongo.db.follower.find_one({
            "who_id": str(g.user['_id']),
            "whom_id": str(profile_user['_id'])
        })
        followed = record is not None
        
    return render_template('timeline.html', messages=messages, 
                           followed=followed, profile_user=profile_user)

@app.route('/<username>/follow')
def follow_user(username):
    if not g.user:
        abort(401)
    whom_user = mongo.db.user.find_one({"username": username})
    if whom_user is None:
        abort(404)
    
    mongo.db.follower.insert_one({
        "who_id": str(g.user['_id']),
        "whom_id": str(whom_user['_id'])
    })
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    if not g.user:
        abort(401)
    whom_user = mongo.db.user.find_one({"username": username})
    if whom_user is None:
        abort(404)
        
    mongo.db.follower.delete_one({
        "who_id": str(g.user['_id']),
        "whom_id": str(whom_user['_id'])
    })
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/add_message', methods=['POST'])
def add_message():
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        mongo.db.message.insert_one({
            'author_id': session['user_id'],
            'username': g.user['username'],
            'email': g.user['email'],
            'text': request.form['text'],
            'pub_date': int(time.time()),
            'flagged': 0
        })
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = mongo.db.user.find_one({"username": request.form['username']})
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = str(user['_id'])
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = mongo.db.user.find_one({"username": request.form['username']})
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif user is not None:
            error = 'The username is already taken'
        else:
            mongo.db.user.insert_one({
                'username': request.form['username'],
                'email': request.form['email'],
                'pw_hash': generate_password_hash(request.form['password'])
            })
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))


# add some filters to jinja and set the secret key and debug mode
# from the configuration.
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
app.secret_key = SECRET_KEY
app.debug = DEBUG


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)