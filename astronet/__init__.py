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
   
app = Flask(__name__)

from astronet.api import api, post, get_posts
app.register_blueprint(api, url_prefix='/api')

app.config.from_object(__name__)

from helpers import *
from account import *

@app.route('/')
def home():
    """ Return the homepage with all the posts """
    posts = json.loads(get_posts().data)['posts']
    return render_template('home.html', posts=posts)

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
