from ..api import api, auth_required
from ..helpers import gen_filename

class Tree_element:
    def __init__(self, comment_toset=None):
        self.children = []
        self.comment = comment_toset
    
    def __repr__(self):
        ret = 'Children: '
        for child in self.children:
            ret += child + ' '
        ret += '\n'
        ret += 'Comment: ' + self.comment + '\n\n'
        return ret

def generate_tree(comments):
    """ Generates a hierarchical comments list. What it does is inverting
        a linked list of comments to point from root to leafs and not
        from leaf to the root and returns the list
    """
    tree = []
    tree_hash = {}
    tree.append(Tree_element())
    for comment in comments:
        tree.append(Tree_element(comment))
        # We cache the location of this comment id
        tree_hash[comment['string_id']] = len(tree)-1

        # If somebody had posted this comment as a reply
        if comment['parent']:
            tree[tree_hash[comment['reply_to']]].children.append(len(tree)-1)
    return tree

@api.route('/comments/<post_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@auth_required
def comments(post_id):
    if request.method == 'GET':
        comments = query_db('SELECT string_id, author, parent, '
                'timestamp, body FROM comments WHERE post=%s',[post_id])
        if len(comments) == 0:
            return jsonify(status='db_null_error')
        return jsonify(status='succ', posts=generate_tree(comments))

    if request.method == 'POST':
        f = request.form
        if not 'parent' in f:
            f['parent'] = None

        if len(f['body'].strip()) > 1000:
            return jsonify(status='db_constraints_error', field='body')
        ret = query_db('INSERT INTO comments (string_id, author, parent'
                ',post, body) VALUES (%s,%s,%s,%s,%s)',
                [gen_filename(), g.uid, f['parent'], post_id, f['body']])
        if ret == 1:
            return jsonify(status='succ')
        elif ret == -1:
            return jsonify(status='db_constraints_error')
        return jsonify(status='db_error')


