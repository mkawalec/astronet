from ..api import api, auth_required, query_db, gen_filename
from flask import (request, g, jsonify, abort)

from markdown import markdown

@api.route('/post', methods=['POST'])
@api.route('/post/<string_id>')
@auth_required
def post(post=None, string_id=None):
    """ Saves or gets a post """
    if request.method == 'GET' and string_id:
        ret = query_db('SELECT author, title, body FROM posts WHERE '
                       'draft=FALSE AND string_id=%s', (string_id,),
                       one=True)
        if ret == None:
            return jsonify(status='db_null_error')
        return jsonify(status='succ', post=ret)
    elif request.method == 'POST':
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
    ret = query_db('SELECT author, title, lead, string_id FROM posts WHERE '
                   'draft=FALSE ORDER BY id DESC')
    return jsonify(status='succ', posts=ret)
