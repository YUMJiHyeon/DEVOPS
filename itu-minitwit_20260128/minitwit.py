# -*- coding: utf-8 -*
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import re
import os
import time
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId


PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'
MONGO_URI = "mongodb://68.183.13.121:27017/minitwit"
DATABASE_NAME = "minitwit"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'development key'

def get_db():
    if 'db' not in g:
        client = MongoClient(MONGO_URI)
        g.db = client[DATABASE_NAME]
    return g.db

@app.before_request
def before_request():
    g.db = get_db()
    g.user = None
    if 'user_id' in session:
        g.user = g.db.user.find_one({"_id": ObjectId(session['user_id'])})

@app.after_request
def after_request(response):
    return response

def get_user_id(username):
    rv = g.db.user.find_one({"username": username}, {"_id": 1})
    return rv['_id'] if rv else None

def format_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

def gravatar_url(email, size=80):
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)

app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url

@app.route('/')
def timeline():
    print(("We got a visitor from: " + str(request.remote_addr)))
    if not g.user:
        return redirect(url_for('public_timeline'))
    
    following = g.db.follower.find({"who_id": g.user['_id']})
    following_ids = [f['whom_id'] for f in following]
    following_ids.append(g.user['_id'])

    messages = list(g.db.message.aggregate([
        {"$match": {"author_id": {"$in": following_ids}, "flagged": 0}},
        {"$lookup": {"from": "user", "localField": "author_id", "foreignField": "_id", "as": "user"}},
        {"$unwind": "$user"},
        {"$sort": {"pub_date": -1}},
        {"$limit": PER_PAGE}
    ]))
    for msg in messages:
        author = g.db.user.find_one({"_id": msg.get("author_id")})
        if author:
            msg['username'] = author.get('username', 'Unknown')
            msg['email'] = author.get('email', '')
        else:
            msg['username'] = 'Unknown'
            msg['email'] = ''
    return render_template('timeline.html', messages=messages)

@app.route('/public')
def public_timeline():
    messages = list(g.db.message.aggregate([
        {"$match": {"flagged": 0}},
        {"$lookup": {"from": "user", "localField": "author_id", "foreignField": "_id", "as": "user"}},
        {"$unwind": "$user"},
        {"$sort": {"pub_date": -1}},
        {"$limit": PER_PAGE}
    ]))
    for msg in messages:
        author = g.db.user.find_one({"_id": msg.get("author_id")})
        
        if author:
            msg['username'] = author.get('username', 'Unknown')
            msg['email'] = author.get('email', '')
        else:
            msg['username'] = 'Unknown'
            msg['email'] = ''
    return render_template('timeline.html', messages=messages)

@app.route('/<username>')
def user_timeline(username):
    profile_user = g.db.user.find_one({"username": username})
    if profile_user is None:
        abort(404)
    
    followed = False
    if g.user:
        followed = g.db.follower.find_one({
            "who_id": g.user['_id'], 
            "whom_id": profile_user['_id']
        }) is not None

    messages = list(g.db.message.aggregate([
        {"$match": {"author_id": profile_user['_id'], "flagged": 0}},
        {"$lookup": {"from": "user", "localField": "author_id", "foreignField": "_id", "as": "user"}},
        {"$unwind": "$user"},
        {"$sort": {"pub_date": -1}},
        {"$limit": PER_PAGE}
    ]))
    for msg in messages:
        msg['username'] = profile_user.get('username', 'Unknown')
        msg['email'] = profile_user.get('email', '')

    return render_template('timeline.html', messages=messages, followed=followed, profile_user=profile_user)

@app.route('/<username>/follow')
def follow_user(username):
    if not g.user: abort(401)
    whom_id = get_user_id(username)
    if whom_id is None: abort(404)
    
    g.db.follower.update_one(
        {"who_id": g.user['_id'], "whom_id": whom_id},
        {"$set": {"who_id": g.user['_id'], "whom_id": whom_id}},
        upsert=True
    )
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))

@app.route('/<username>/unfollow')
def unfollow_user(username):
    if not g.user: abort(401)
    whom_id = get_user_id(username)
    if whom_id is None: abort(404)
    
    g.db.follower.delete_one({"who_id": g.user['_id'], "whom_id": whom_id})
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))

@app.route('/add_message', methods=['POST'])
def add_message():
    if 'user_id' not in session: abort(401)
    if request.form['text']:
        g.db.message.insert_one({
            "author_id": g.user['_id'],
            "text": request.form['text'],
            "pub_date": int(time.time()),
            "flagged": 0
        })
        flash('Your message was recorded')
    return redirect(url_for('timeline'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user: return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = g.db.user.find_one({"username": request.form['username']})
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error = 'Invalid password'
        else:
            session['user_id'] = str(user['_id'])
            flash('You were logged in')
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user: return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password') or data.get('pwd')

        if not username: error = 'You have to enter a username'
        elif not email or '@' not in email: error = 'Invalid email address'
        elif not password: error = 'You have to enter a password'
        elif g.db.user.find_one({"username": username}):
            if request.is_json: return '', 204 # 시뮬레이터 중복 가입 대응
            error = 'The username is already taken'
        else:
            g.db.user.insert_one({
                "username": username, "email": email,
                "pw_hash": generate_password_hash(password)
            })
            if request.is_json: return '', 204
            flash('You were successfully registered')
            return redirect(url_for('login'))
        
        if request.is_json: return error, 400
    return render_template('register.html', error=error)

@app.route('/msgs/<username>', methods=['POST'])
def add_message_api(username):
    data = request.get_json(silent=True) or request.form
    text = data.get('content')
    user = g.db.user.find_one({"username": username})
    if not user: return "User not found", 404
    if not text: return "No content", 400

    g.db.message.insert_one({
        "author_id": user['_id'],
        "text": text,
        "pub_date": int(time.time()),
        "flagged": 0
    })
    return '', 204

@app.route('/fllws/<username>', methods=['POST'])
def follow_user_api(username):
    data = request.get_json(silent=True) or request.form
    user = g.db.user.find_one({"username": username})
    if not user: 
        return "User not found", 404

    if 'follows' in data:
        whom_username = data['follows']
        whom = g.db.user.find_one({"username": whom_username})
        if not whom:
            return "Followed user not found", 404
        
        g.db.follower.update_one(
            {"who_id": user['_id'], "whom_id": whom['_id']},
            {"$set": {"who_id": user['_id'], "whom_id": whom['_id']}},
            upsert=True
        )
        return '', 204

    elif 'unfollows' in data:
        whom_username = data['unfollows']
        whom = g.db.user.find_one({"username": whom_username})
        if not whom:
            return "Unfollowed user not found", 404
        
        g.db.follower.delete_one({"who_id": user['_id'], "whom_id": whom['_id']})
        return '', 204

    return "Invalid request", 400

@app.route('/logout')
def logout():
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
