# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
# Triggering CI/CD pipeline recording

import re
import os, shutil
import time
import sqlite3
from hashlib import md5
from datetime import datetime, timezone
from contextlib import closing
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

metrics_dir = os.environ.get('PROMETHEUS_MULTIPROC_DIR', '/app/prometheus_metrics')

os.makedirs(metrics_dir, mode=0o755, exist_ok=True)

# configuration
DATABASE = '/tmp/minitwit.db'
PER_PAGE = 30
DEBUG = False
SECRET_KEY = 'development key'
TWEET_COUNT = Counter('minitwit_tweets_total', 'Total number of tweets posted')
USER_COUNT = Gauge('minitwit_users_total', 'Total registered users in DB')
FOLLOWER_COUNT = Gauge('minitwit_followers_total', 'Total follow relationships in DB')
REGISTER_TEMPLATE = 'register.html'

# create our little application :)
app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/minitwit")
app.config["SECRET_KEY"] = 'development key'
app.config["DEBUG"] = True

mongo = PyMongo(app)

metrics = GunicornInternalPrometheusMetrics(app, path="/metrics")

def update_db_counts():
    try:
        USER_COUNT.set(mongo.db.user.count_documents({}))
        FOLLOWER_COUNT.set(mongo.db.follower.count_documents({}))
    except Exception as e:
        print(f"Error updating counts: {e}")

user_count_gauge = Gauge("minitwit_user_count", "Total number of users")

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
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d @ %H:%M')

def gravatar_url(email, size=80):
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = mongo.db.user.find_one({"_id": ObjectId(session['user_id'])})
    if request.path == "/metrics":
        update_db_counts()


@app.route('/')
def timeline():
    if not g.user:
        return redirect(url_for('public_timeline'))
    messages = query_db('message', limit=PER_PAGE)
    return render_template('timeline.html', messages=messages)

@app.route('/public', methods=['GET'])
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
    
    return "", 204

@app.route('/<username>', methods=['GET'])
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

@app.route('/<username>/follow', methods=['GET'])
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


@app.route('/<username>/unfollow', methods=['GET'])
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


@app.route("/login", methods=["GET"])
def login():
    if g.user:
        return redirect(url_for("timeline"))

    return render_template("login.html", error=None)


@app.route("/login", methods=["POST"])
def login_post():
    if g.user:
        return redirect(url_for("timeline"))

    error = None
    user = mongo.db.user.find_one({"username": request.form["username"]})

    if user is None:
        error = "Invalid username"
    elif not check_password_hash(user["pw_hash"], request.form["password"]):
        error = "Invalid password"
    else:
        flash("You were logged in")
        session["user_id"] = str(user["_id"])
        return redirect(url_for("timeline"))

    return render_template("login.html", error=error)

def validate_register_input(username, email, password):
    if not username:
        return 'You have to enter a username'
    if not email or '@' not in email:
        return 'You have to enter a valid email address'
    if not password:
        return 'You have to enter a password'
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('timeline'))

    if request.method == 'GET':
        return render_template(REGISTER_TEMPLATE, error=None)

    data = request.get_json(silent=True) or request.form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password') or data.get('pwd')
    is_api = request.is_json or request.args.get('latest')

    error = validate_register_input(username, email, password)
    if error:
        if is_api and error == 'You have to enter a password':
            return "Missing password", 400
        return render_template(REGISTER_TEMPLATE, error=error)
    
    try:
        existing_user = mongo.db.user.find_one({"username": username})
        if not existing_user:
            mongo.db.user.insert_one({
                'username': username,
                'email': email,
                'pw_hash': generate_password_hash(password) 
            })

        if is_api:
            return "", 204
                        
        if existing_user:
            return render_template(REGISTER_TEMPLATE, error='The username is already taken')
        
        flash('You were successfully registered')
        return redirect(url_for('login'))
    
    except Exception as e:
            print(f"DEBUG: Register error - {e}")
            return str(e), 500
            
@app.route('/logout', methods=['GET'])
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
    app.run(host="127.0.0.1", port=5000)
