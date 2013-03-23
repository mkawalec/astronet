from . import app
from flask import (request, g, jsonify, abort)
from .helpers import (stringify, stringify_class, db_commit,
        FoundExc, get_user, gen_filename, auth_required)

from markdown import markdown
from functools import wraps

from .database import db_session
from .models import Post, User
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

@app.route('/post/<post_id>', methods=['GET', 'PUT', 'DELETE'])
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

@app.route('/post/<post_id>/authors', methods=['GET', 'PUT', 'DELETE', 'POST'])
@prepare_post
def post_authors(string_id, post, user):
    ''' Updates, gets or deletes post authors '''
    
    if request.method == 'GET':
        return jsonify(authors=stringify_class(post.authors))

    elif request.method == 'DELETE':
        # Remove all the authors matching the criteria 
        # from the authors list
        for aid in request.form.getlist('ids[]'):
            for author in post.authors:
                if author.string_id == aid:
                    post.authors.remove(author)
                    break
        return db_commit()

    elif request.method == 'PUT':
        users = db_session.query(User).\
                filter(User.string_id.in_(request.form.getlist('ids[]'))).\
                all()
        post.authors = users
        return db_commit()

    elif request.method == 'POST':
        users = db_session.query(User).\
                filter(User.string_id.in_(request.form.getlist('ids[]'))).\
                all()
        post.authods.extend(users)
        return db_commit()


@app.route('/post', methods=['POST'])
@auth_required
@get_user
def save_post(user):
    ''' Saves a post '''
    f = request.form

    post = Post(f['title'], f['body'])
    if 'draft' in f and f['draft'] == False:
        post.draft = False 

    db_session.add(post)
    db_session.flush()

    post.authors.append(user)
    return db_commit(post)

@app.route('/post/preview', methods=['POST'])
@auth_required
def post_preview():
    """ Gets a markdown post preview """
    return jsonify(status='succ', preview=markdown(request.form['body']))

@app.route('/posts/<author_id>')
@app.route('/posts')
@get_user
def get_posts(user=None, author_id=None):
    ''' Return all posts by a given author or just all
        posts generally '''
    posts = db_session.query(Post).\
            options(joinedload(Post.authors)).\
            filter(Post.disabled == False)

    if author_id:
        posts = posts.\
                join(User).filter(User.string_id == author_id)

    if bool(request.args.get('draft')) == True:
        if not user:
            abort(403)
        if user.role != 'admin':
            if author_id and author_id != user.string_id:
                abort(403)
            posts = posts.\
                    join(Post.authors).filter(User.string_id == user.string_id)
        posts = posts.filter(Post.draft == True)
    else:
        posts = posts.filter(Post.draft == False)

    limit = request.args.get('limit')
    if not limit or limit > 30:
        limit = 30

    after = request.args.get('after')
    if after:
        stmt = db_session.query(User).\
                filter(User.string_id == after).\
                subquery()

        posts = posts.\
                filter(Post.id > stmt.c.id)
    
    posts = posts.\
            order_by(desc(Post.timestamp)).\
            limit(limit).\
            all()

    return jsonify(status='succ', posts=stringify_class(posts))
