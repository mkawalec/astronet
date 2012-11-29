from ..api import api, auth_required, query_db
from flask import (request, g, jsonify, abort)

from markdown import markdown

@api.route('/post', methods=['POST'])
@auth_required
def post():
    # We want to save a post
    if request.method == 'POST':
        ret = query_db('INSERT INTO posts (author, title, lead, body) '
                       'VALUES (%s, %s, %s, %s)',
                       (g.uid, request.form['title'], request.form['lead'],
                           request.form['body']))
        if ret == 1:
            return jsonify(status='succ')
        elif ret == -1:
            return jsonify(status='db_constraints_error')
        return jsonify(status='db_error')

@api.route('/post/preview', methods=['POST'])
@auth_required
def post_preview():
    return jsonify(status='succ', preview = markdown(request.form['post_body']))
