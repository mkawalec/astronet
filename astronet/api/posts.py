from ..api import api, auth_required, query_db, gen_filename
from flask import (request, g, jsonify, abort)
from ..helpers import stringify

from markdown import markdown

@api.route('/post/<string_id>')
def post(post=None, string_id=None):
    """ Saves or gets a post """
    if string_id:
        ret = query_db('SELECT u.real_name AS author, p.title, p.body, p.string_id, '
                       'p.timestamp, p.visits FROM posts p, users u WHERE '
                       'p.draft=FALSE AND p.string_id=%s AND u.id=p.author', 
                       [string_id], one=True)
        if ret == None:
            return jsonify(status='db_null_error')

        ret['body'] = markdown(ret['body'])
        ret = stringify(ret, one=True)

        # Save the stats
        query_db('UPDATE posts SET visits=visits+1 WHERE string_id=%s',
                [string_id])

        return jsonify(status='succ', post=ret)

@api.route('/post', methods=['POST', 'PUT'])
@auth_required
def save_post(post=None):
    if post == None:
        post = request.form
    ret = None
    print post

    if request.method == 'POST':
        ret = query_db('INSERT INTO posts (author, title, lead, '
                       'body, string_id) '
                       'VALUES (%s, %s, %s, %s, %s)',
                       (g.uid, post['title'], post['lead'],
                        post['body'], gen_filename()))
    elif request.method == 'PUT':
        ret = query_db('UPDATE posts SET title=%s, lead=%s, body=%s '
                       'WHERE string_id=%s AND author=%s',
                       (post['title'], post['lead'], post['body'],
                       post['string_id'], g.uid))
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

@api.route('/posts/<author>')
@api.route('/posts')
def get_posts(author=None):
    """ Returns all posts visible to the user """
    if not author:
        ret = query_db('SELECT u.real_name AS author, p.title, p.lead, p.string_id, '
                       'p.timestamp, p.body, comments_count(p.string_id) '
                       'FROM posts p, users u WHERE '
                       'p.draft=FALSE AND u.id=p.author ORDER BY p.id DESC')
    else:
        ret = query_db('SELECT u.real_name AS author, p.title, p.lead, p.string_id, '
                       'p.timestamp, p.body, comments_count(p.string_id) '
                       'FROM posts p, users u '
                       'WHERE p.author=u.id AND u.string_id=%s AND draft=FALSE '
                       'ORDER BY p.id DESC', [author])
    ret = stringify(ret)
    return jsonify(status='succ', posts=ret)


@api.route('/drafts/<author>')
@api.route('/drafts')
def get_drafts(author=None):
    """ Returns all posts visible to the user """
    if not author:
        ret = query_db('SELECT author, title, lead, string_id FROM posts WHERE '
                   'draft=TRUE ORDER BY id DESC')
    else:
        ret = query_db('SELECT p.author, p.title, p.lead FROM posts p, users u '
                   'WHERE p.author=u.id AND u.string_id=%s AND draft=TRUE '
                   'ORDER BY p.id DESC', (author,))
    return jsonify(status='succ', drafts=ret)
