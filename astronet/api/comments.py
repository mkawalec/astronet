# coding=utf-8
from ..api import api, auth_required
from ..helpers import gen_filename, query_db
from flask import request, jsonify,g 

class TreeElement:
    def __init__(self, comment_toset=None):
        self.children = []
        self.comment = comment_toset

    def serialize(self):
        d = dict()
        d['children'] = self.children
        d['comment'] = self.comment
        if d['comment'] != None:
            d['comment']['timestamp'] = str(d['comment']['timestamp'])

        return d

def generate_tree(comments):
    """ Generates a hierarchical comments list. What it does is inverting
        a linked list of comments to point from root to leafs and not
        from leaf to the root and returns the list
    """
    tree = []
    tree_hash = {}
    tree.append(TreeElement())
    for comment in comments:
        tree.append(TreeElement(comment))
        # We cache the location of this comment id
        tree_hash[comment['string_id']] = len(tree)-1

        # If somebody had posted this comment as a reply
        if comment['parent']:
            tree[tree_hash[comment['parent']]].children.append(len(tree)-1)
        else:
            tree[0].children.append(len(tree)-1)

    ret = []
    for comment in tree:
        ret.append(comment.serialize())
    return ret

@api.route('/comments/<post_id>', methods=['POST', 'PUT'])
@auth_required
def comments(post_id=None):
    if request.method == 'POST':
        f = dict(request.form)
        if not 'parent' in f or f['parent'][0] == 'null' \
                or len(f['parent'][0]) == 0:
            f['parent'][0] = None

        if len(f['body'][0].strip()) > 1000:
            return jsonify(status='db_constraints_error', field='body')

        string_id = gen_filename()
        ret = query_db('INSERT INTO comments (string_id, author, parent'
                ',post, body) VALUES (%s,%s,%s,%s,%s)',
                [string_id, g.uid, f['parent'][0], post_id, f['body'][0]])
        if ret == 1:
            return jsonify(status='succ', string_id=string_id)
        elif ret == -1:
            return jsonify(status='db_constraints_error')
        return jsonify(status='db_error')

    if request.method == 'PUT':
        f = request.form
        ret = query_db ('SELECT update_comment(%s, %s, %s)',
                [f['string_id'].strip(), session['uid'], f['body']],
                one=True)
        if ret == 1:
            return jsonify(status='succ')
        elif ret == -1:
            return jsonify(status='db_null_error')
        return jsonify(status='not_authorized')

@api.route('/comments/<post_id>')
def show_comments(post_id):
    comments = query_db('SELECT string_id, author, parent, '
            'timestamp, body FROM comments WHERE post=%s '
            'ORDER BY id ASC',[post_id])
    if len(comments) == 0:
        return jsonify(status='db_null_error')
    return jsonify(status='succ', comments=generate_tree(comments))

@api.route('/comment/<comment_id>', methods=['GET', 'DELETE'])
@auth_required
def comment(comment_id):
    if request.method == 'DELETE':
        ret = query_db('SELECT delete_comment(%s, %s)',
                [comment_id.strip(), g.uid], one=True)['delete_comment']
        print ret, comment_id, len(comment_id)
        if ret == 1:
            return jsonify(status='succ')
        elif ret == -1:
            return jsonify(status='db_null_error')
        return jsonify(status='not_authorized')

    elif request.methods == 'GET':
        ret = query_db('SELECT string_id, author, parent, '
                'timestamp, body FROM comments WHERE string_id=%s',
                [comment_id], one=True)
        return jsonify(status='succ', comment=ret)

