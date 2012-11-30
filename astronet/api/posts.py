from ..api import api, auth_required, query_db
from flask import (request, g, jsonify, abort)

from markdown import markdown

@api.route('/post', methods=['POST'])
@auth_required
def post(post=None):
    """ Saves a post """
    if request.method == 'POST':
        if post == None:
            post = request.form

        ret = query_db('INSERT INTO posts (author, title, lead, body, string_id) '
                       'VALUES (%s, %s, %s, %s, %s)',
                       (g.uid, post['title'], post['lead'],post['body'], gen_filename()))
        if ret == 1:
            return jsonify(status='succ')
        elif ret == -1:
            return jsonify(status='db_constraints_error')
        return jsonify(status='db_error')

@api.route('/post/preview', methods=['POST'])
@auth_required
def post_preview():
    """ Gets a markdown post preview """
    return jsonify(status='succ', preview=markdown(request.form['post_body']))

@api.route('/posts')
def get_posts():
    ret = query_db('SELECT author, title, lead FROM posts WHERE '
                   'draft=FALSE ORDER BY id DESC')
    return jsonify(status='succ', posts=ret)
