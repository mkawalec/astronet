# coding=utf-8
from __future__ import division
from flask import (Flask, request, redirect, url_for, abort,
        render_template, flash, jsonify, g, session, send_file)

from astronet import app
from astronet.helpers import login_required, query_db

import json

from datetime import timedelta, datetime
from werkzeug.contrib.atom import AtomFeed

from astronet.api import post, save_post, get_posts

@app.route('/posts.atom')
def atom():
    """ Returns an atom feed with all the posts """
    feed = AtomFeed("Astronet", feed_url=request.url, 
            url=request.host_url,
            subtitle=u'Największy portal astronomiczny w Polsce')
    date = "%Y-%m-%d %H:%M:%S.%f"
    for post in json.loads(get_posts().data)['posts']:
        feed.add(post['title'], summary=post['lead'], summary_type='text',
                 content=markdown(post['body']), content_type='html',
                 author=post['author'], 
                 updated=datetime.strptime(post['timestamp'], date),
                 url=request.host_url+\
                         url_for('show_post', string_id=post['string_id']))
    return feed.get_response()


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
        ret = save_post(request.form).data
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

@app.route('/edit_post/<string_id>')
@login_required
def edit_post(string_id):
    post = query_db('SELECT title, lead, body FROM posts '
                    'WHERE string_id=%s', (string_id,), one=True)
    return render_template('add_post.html', string_id=string_id, 
                                            title=post['title'],
                                            lead=post['lead'],
                                            body=post['body'])
