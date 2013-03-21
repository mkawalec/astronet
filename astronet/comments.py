# coding=utf-8
from . import app
from helpers import (gen_filename, stringify, 
        db_commit, stringify_class, auth_required)
from flask import request, jsonify,g 

from database import db_session
from models import Comment, Post, User
from sqlalchemy.orm.exc import NoResultFound

class TreeElement:
    def __init__(self, comment=None):
        self.children = []
        self.comment = comment

    def __repr__(self):
        return unicode(self.comment)

    def serialize(self):
        ret = {}
        ret['children'] = self.children
        ret['author_id'] = self.comment.author.string_id
        ret['timestamp'] = self.comment.timestamp
        ret['edition_timestamp'] = self.comment.edition_timestamp
        ret['string_id'] = self.comment.string_id

        if self.comment.disabled:
            ret['body'] = 'Deleted'
        else:
            ret['body'] = self.comment.body

        return ret

def generate_tree(comments):
    """ Generates a hierarchical comments list. What it does is inverting
        a tree of comments to point from root to leafs and not
        from leaf to the root and returns the list
    """
    tree = []
    tree_hash = {}
    tree.append(TreeElement())
    for comment in comments:
        tree.append(TreeElement(comment))
        # We cache the location of this comment id
        tree_hash[comment.id] = len(tree)-1

        # If somebody had posted this comment as a reply
        if comment.parent_id:
            tree[tree_hash[comment.parent_id]].children.append(len(tree)-1)
        else:
            tree[0].children.append(len(tree)-1)

    ret = []
    for comment in tree:
        ret.append(comment.serialize())
    return ret

@app.route('/comment/<comment_id>', 
        methods=['POST', 'PUT', 'GET', 'DELETE'])
@auth_required
def comments(comment_id=None):
    if request.method == 'POST':
        f = request.form

        try:
            author = db_sesson.query(User).\
                    filter(User.string_id == g.string_id).one()
        except NoResultFound:
            abort(500)

        try:
            post = db_session.query(Post).\
                    filter(Post.string_id == f['post_id']).one()
        except NoResultFound:
            abort(409)

        parent = None
        if 'parent_id' in f:
            try:
                parent = db_session.query(Comment).\
                        filter(Comment.string_id == f['parent_id']).\
                        one()
            except NoResultFound:
                abort(409)
                    
        comm = Comment(f['body'], author, post, parent)
        db_session.add(comm)
        return db_commit()

    try:
        comment = db_session.query(Comment).\
                filter(Comment.disabled == False).\
                filter(Comment.string_id == comment_id).one()
        user = db_session.query(User).\
                filter(User.string_id == g.string_id).one()
        if user.role != 'admin':
            if comment.author_id != user.id:
                abort(403)
    except NoResultFound:
        abort(404)

    if request.method == 'PUT':
        for param in request.form:
            comment.__dict__[param] = request.form[param]
            return db_commit()

    elif request.method == 'DELETE':
        comment.disabled == True
        return db_commit()

    elif request.method == 'GET':
        return jsonify(status='succ', 
                comment=stringify_class(comment, one=True))


@app.route('/comments/<post_id>')
def show_comments(post_id):
    comms = db_session.query(Comment).\
            options(joinedload(Comment.author)).\
            join(Post).\
            filter(Post.string_id == post_id).all()
    return jsonify(status='succ', comments=generate_tree(comms))

