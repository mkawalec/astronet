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

# Rewritten from this site (http://flask.pocoo.org/snippets/44/); dunno what macros do and %- operator
@app.route('/', defaults={'page': 1})
@app.route('/<int:page>/')
def home(page):
    """ Return the homepage with all the posts """
    per_page = 10 # to configuration file?
    posts = json.loads(get_posts().data)['posts']
    count = len(posts)
    pagination = Pagination(page, per_page, count)
    posts = posts[(page-1)*per_page:(page)*per_page]
    return render_template('home.html', posts=posts, pagination=pagination)

@app.route('/user', methods=['GET', 'POST'])
@login_required
def show_profile():
    """ Shows user's profile. He can manage it in here, see his posts,
        statistic, drafts(?) change password, email etc. """
    posts = query_db('SELECT author, title, lead, draft, string_id FROM posts '
                     'WHERE author=%s', (session['uid'],))
    return render_template('profile.html', posts=posts,
            real_name=session["real_name"], email=session["email"])

@app.route('/reports/')
@app.route('/reports/<string_id>')
@login_required
def show_reports(string_id=None):
    """ Shows reports. Allows to manage reports (edit posts, 
    correct errors). """
    if session['role'] != 'admin':
        flash(u'Nie masz wystarczających uprawnień.', 'error')
        return redirect(url_for('home'))
    if string_id == None:
        reports = query_db('SELECT r.id, u.real_name as author, r.type, ' 
        'r.timestamp, r.string_id FROM reports r, users u WHERE r.done=False AND '
        'author=r.author ORDER BY timestamp')
        return render_template('reports.html', reports=reports)
    else:
        report = query_db('SELECT u.real_name as real_name, '
        ' p.title as title, r.string_id, r.type, r.body, r.timestamp '
        ' FROM reports r, users u, posts p WHERE r.string_id=%s LIMIT 1'
        ,(string_id,), one=True)
        return render_template('show_report.html', report=report)
    #TODO deleting reports and making them done; also showing done
    #TODO redirecting to editing post


