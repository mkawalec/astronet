from ..api import api, auth_required
from flask import (request, g, jsonify, abort)
from ..helpers import (stringify, stringify_class, db_commit,
        FoundExc, get_user, gen_filename)

from markdown import markdown
from functools import wraps

from ..database import db_session
from ..models import Post, User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

def prepare_post(f):
    @wraps(f)
    def fn(*args, **kwargs):
        try:
            post = db_session.query(Post).\
                options(joinedload(Post.authors)).\
                filter(Post.string_id == kwargs['post_id']).one()
            if request.method != 'GET':
                if not g.string_id:
                    abort(403)
                try:
                    user = db_session.query(User).\
                        filter(User.string_id == g.string_id).one()
                except NoResultFound:
                    abort(409)

                # Check if the currently accessing user has the rights
                # to modify this post
                if user.role != 'admin':
                    for author in post.authors:
                        if author.string_id == g.string_id:
                            raise FoundExc()
                    abort(403)
        except NoResultFound:
            abort(404)
        except FoundExc:
            pass
        return f(*args, post=post, user=user, **kwargs)
    return fn

@api.route('/post/<post_id>', methods=['GET', 'PUT', 'DELETE'])
@prepare_post
def post(post_id, post, user):
    """ Updates, gets or deletes a post """
    if request.method == 'GET':
        return jsonify(post=stringify_class(post, one=True))

    elif request.method == 'DELETE':
        post.disabled = True
        return db_commit()

    elif request.method == 'PUT':
        for prop in request.form:
            post.__dict__[prop] = request.form[prop]
        return db_commit()

@api.route('/post/<post_id>/authors', methods=['GET', 'PUT', 'DELETE', 'POST'])
@prepare_post
def post_authors(string_id, post, user):
    ''' Updates, gets or deletes post authors '''
    
    if request.method == 'GET':
        return jsonify(authors=stringify_class(post.authors))

    elif request.method == 'DELETE':
        # Remove all the authors matching the criteria 
        # from the authors list
        for aid in request.form.getlist('ids'):
            for author in post.authors:
                if author.string_id == aid:
                    post.authors.remove(author)
                    break
        return db_commit()

    elif request.method == 'PUT':
        users = db_session.query(User).\
                filter(User.string_id.in_(request.form.getlist('ids'))).\
                all()
        post.authors = users
        return db_commit()

    elif request.method == 'POST':
        users = db_session.query(User).\
                filter(User.string_id.in_(request.form.getlist('ids'))).\
                all()
        post.authods.extend(users)
        return db_commit()


@api.route('/post', methods=['POST'])
@auth_required
@get_user
def save_post(user):
    ''' Saves a post '''
    f = request.form

    post = Post(f['title'], f['body'])
    if f['draft'] == False:
        post.draft = False 

    db_session.add(post)
    db_session.flush()

    post.authors.append(user)
    return db_commit()



@api.route('/post/preview', methods=['POST'])
@auth_required
def post_preview():
    """ Gets a markdown post preview """
    return jsonify(status='succ', preview=markdown(request.form['body']))

@api.route('/posts/<author_id>')
@api.route('/posts')
def get_posts(author_id=None):
    ''' Return all posts by a given author or just all
        posts generally '''
    posts = db_session.query(Post).\
            filter(Post.disabled == False)

    if author_id:
        posts = posts.filter(Post.string_id == author_id) 
    if request.args.get('drafts') == True:
        posts = posts.filter(Post.draft == True)
    else:
        posts = posts.filter(Post.draft == False)

    posts = posts.\
            order_by(desc(Post.edition_timestamp)).\
            all()

    return jsonify(status='succ', posts=posts)
