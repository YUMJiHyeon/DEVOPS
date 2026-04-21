# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import re
import os, shutil
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
from prometheus_flask_exporter import PrometheusMetrics 
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

metrics_dir = os.environ.get('PROMETHEUS_MULTIPROC_DIR', '/app/prometheus_metrics')
if os.path.exists(metrics_dir):
    shutil.rmtree(metrics_dir)
os.makedirs(metrics_dir, mode=0o755, exist_ok=True)

# configuration
DATABASE = '/tmp/minitwit.db'
PER_PAGE = 30
DEBUG = False
SECRET_KEY = 'development key'
TWEET_COUNT = Counter('minitwit_tweets_total', 'Total number of tweets posted')
USER_COUNT = Gauge('minitwit_users_total', 'Total registered users in DB')
FOLLOWER_COUNT = Gauge('minitwit_followers_total', 'Total follow relationships in DB')

# create our little application :)
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://groupo:devopsgroupo@68.183.13.121:27017/minitwit?authSource=admin"
app.config["SECRET_KEY"] = 'development key'
app.config["DEBUG"] = True

mongo = PyMongo(app)

metrics = GunicornPrometheusMetrics(app, path=None)

def update_db_counts():
    try:
        USER_COUNT.set(mongo.db.user.count_documents({}))
        FOLLOWER_COUNT.set(mongo.db.follower.count_documents({}))
    except Exception as e:
        print(f"Error updating counts: {e}")

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

@app.route('/msgs/<username>', methods=['POST'])
def add_message_by_username(username):
    print(f"DEBUG: Attempting to tweet for user: {username}")
    data = request.get_json() if request.is_json else request.form
    user = mongo.db.user.find_one({"username": username})
    if not user:
        return "User not found", 404

    mongo.db.message.insert_one({
        'author_id': str(user['_id']), 
        'text': data.get('content') or data.get('text'), 
        'pub_date': int(time.time()),
        'username': user['username'], 
        'email': user['email']
    })
    TWEET_COUNT.inc()
    return "", 204

@app.route('/fllws/<username>', methods=['POST'])
def follow_user_api(username):
    data = request.get_json() if request.is_json else request.form
    
    return "", 204

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
        TWEET_COUNT.inc() 
        update_db_counts() 
        flash('Your message was recorded')
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
        data = request.get_json(silent=True) or request.form
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password') or data.get('pwd')

        if not username:
            error = 'You have to enter a username'
        elif not email or '@' not in email:
            error = 'You have to enter a valid email address'
        elif not password:
            if request.is_json or request.args.get('latest'):
                return "Missing password", 400
            error = 'You have to enter a password'
        else:
            try:
                existing_user = mongo.db.user.find_one({"username": username})
                if not existing_user:
                    mongo.db.user.insert_one({
                        'username': username,
                        'email': email,
                        'pw_hash': generate_password_hash(password) # 이제 password가 None이 아니므로 안전함!
                    })
                
                if request.is_json or request.args.get('latest'):
                    return "", 204
                
                if existing_user:
                    error = 'The username is already taken'
                else:
                    flash('You were successfully registered')
                    return redirect(url_for('login'))
            except Exception as e:
                print(f"DEBUG: Register error - {e}")
                return str(e), 500
            
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))

@app.route('/metrics')
def metrics_with_update():
    try:
        user_count = mongo.db.user.count_documents({})
        USER_COUNT.set(user_count)
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        app.logger.error(f"Metrics update failed: {e}")
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


# add some filters to jinja and set the secret key and debug mode
# from the configuration.
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
app.secret_key = SECRET_KEY
app.debug = DEBUG



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)