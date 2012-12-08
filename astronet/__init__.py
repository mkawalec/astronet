# coding=utf-8
from __future__ import division
from flask import (Flask, request, redirect, url_for, abort,
        render_template, flash, jsonify, g, session, send_file)

from datetime import timedelta

import json

SECRET_KEY = 'ddsnfkrjoireklfjdslkiro43213213m5,tsrfdeldmfxruc'
SALT = 'nfkren<F4><F4>ffdsdsdfdewdsdfvvv'
PERMANENT_SESSION_LIFETIME = timedelta(days=30)
DB = 'astronet'
TRAP_BAD_REQUEST_ERRORS = False
   
app = Flask(__name__)

from astronet.api import api, post, get_posts, get_drafts
app.register_blueprint(api, url_prefix='/api')

app.config.from_object(__name__)

from helpers import *
from account import *

@app.route('/')
def home():
    """ Return the homepage with all the posts """
    posts = json.loads(get_posts().data)['posts']
    return render_template('home.html', posts=posts)

@app.route('/post/<string_id>')
def show_post(string_id):
    """ Show a post with a given id """
    news = json.loads(post(string_id=string_id).data)
    if news['status'] == 'succ':
        return render_template('show_post.html', post=news['post'])
    else:
        flash(u'Błąd przy pobieraniu posta!', 'error')
        return redirect(url_for('home'))

@app.route('/add_post', methods=['POST', 'GET'])
@login_required
def add_post():
    """ Generate the posts addition template when accessed with **GET** and 
        add a post when accessed with **POST**
    """
    if request.method == 'POST':
        ret = post(request.form).data
        if json.loads(ret)['status'] == 'succ':
            flash(u'Twój post został dodany', 'success')
            return redirect(url_for('home'))
        else:
            flash(u'Nie można było dodać posta')
            return render_template('add_post.html',
                    title=request.form['title'].strip(),
                    lead=request.form['lead'].strip(),
                    body=request.form['body'].strip())

    return render_template('add_post.html')


@app.route('/user', methods=['GET', 'POST'])
@login_required
def show_profile():
    """Shows user's profile. He can manage it in here, see his posts, statistic, drafts(?) change password, email etc. """
    posts = json.loads(get_posts(session['string_id']).data)['posts']
    drafts = json.loads(get_drafts(session['string_id']).data)['drafts']
    return render_template('profile.html',posts=posts, drafts=drafts)
    

    
