# coding=utf-8
from __future__ import division
from flask import (Flask, request, redirect, url_for, abort,
        render_template, flash, jsonify, g, session, send_file)


from markdown import markdown

import json
   
app = Flask(__name__)
app.config.from_pyfile('config.cfg')

from astronet.api import api, post, get_posts, get_drafts
app.register_blueprint(api, url_prefix='/api')

from helpers import *
from account import *
from posts import *

@app.route('/')
def home():
    """ Return the homepage with all the posts """
    posts = json.loads(get_posts().data)['posts']
    return render_template('home.html', posts=posts)

@app.route('/user', methods=['GET', 'POST'])
@login_required
def show_profile():
    """ Shows user's profile. He can manage it in here, see his posts,
        statistic, drafts(?) change password, email etc. """
    posts = query_db('SELECT author, title, lead, draft, string_id FROM posts '
                     'WHERE author=%s', (session['uid'],))
    return render_template('profile.html', posts=posts,
            real_name=session["real_name"], email=session["email"])



        

        
