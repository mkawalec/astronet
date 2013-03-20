# coding=utf-8
from __future__ import division
from flask import (Flask, request, redirect, url_for, abort,
        render_template, flash, jsonify, g, session, send_file)

from .. import app

import json

from datetime import timedelta, datetime
from werkzeug.contrib.atom import AtomFeed

from .api import post, save_post, get_posts

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

