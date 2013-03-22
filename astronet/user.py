from . import app
from flask import (request, render_template, g, jsonify, abort,
        session)

from .database import db_session
from .models import User
from .account import logout
from sqlalchemy.orm.exc import NoResultFound

from .helpers import (db_commit, auth_required,
        stringify_class, get_user, get_string_id)

from datetime import datetime

@app.route('/user/<string_id>')
@app.route('/user')
@get_user
@get_string_id
def get_user_data(user, string_id):
    try:
        got_user = db_session.query(User)

        if user and user.role != 'admin':
            ''' Only admins can see disabled users '''
            got_user = got_user.\
                    filter(User.disabled == False)

        got_user = got_user.\
            filter(User.string_id == string_id).one()
    except NoResultFound:
        abort(404)
    return jsonify(status='succ', user=stringify_class(got_user, one=True))

@app.route('/user/<string_id>', methods=['PUT', 'DELETE', 'POST'])
@app.route('/user', methods=['PUT', 'DELETE'])
@get_user
@get_string_id
def set_user_data(user, string_id):
    ''' Updates the user '''
    if user.role != 'admin' and user.string_id != string_id:
        ''' Only admins can modify different users '''
        abort(403)

    try:
       change_user = db_session.query(User).\
            filter(User.string_id == string_id).one()
    except NoResultFound:
        abort(404)

    if request.method == 'PUT':
        for prop in request.form:
            if prop == 'old_password':
                continue
            elif prop == 'role' and user.role == 'admin':
                setattr(change_user, prop, request.form[prop])
            elif prop == 'salt' or prop == 'activated' or \
                    prop == 'timestamp' or prop == 'disabled' or \
                    prop == 'edition_timestamp' or prop == 'string_id' or \
                    prop == 'id' or prop == 'role':
                        # We don't want people to tinker with these
                        # and we really want to let them know that 
                        # they are not cool
                        abort(409)
                        # TODO: Log this

            elif prop == 'password':
                if not user.update_pass(request.form['old_password'],
                        request.form['password']):
                    # Hey, you provided a wrong old password
                    abort(403)

            elif prop == 'email':
                # TODO: implement
                continue

            else:
                if prop in change_user.__dict__:
                    # Without setting it this way SQLAlchemy will not notice
                    # something had changed :(
                    setattr(change_user, prop, request.form[prop])
                else:
                    abort(400)

        change_user.edition_timestamp = datetime.now()

    elif request.method == 'DELETE':
        change_user.disabled = True
        if user.string_id == string_id:
            logout()

    if request.method == 'POST':
        if user.role != 'admin':
            abort(403)
        change_user.disabled = False

    return db_commit()

@app.route('/users')
def get_users():
    ''' Returns a list of users, with a limit 
        and a starting point provided '''

    limit = request.args.get('limit')
    if not limit or limit > 20:
        limit = 20

    after = request.args.get('after')
    users = db_session.query(User)

    if after:
        stmt = db_session.query(User).\
                filter(User.string_id == after).\
                subquery()
        users = users.\
                filter(User.id > stmt.c.id)

    users = users.limit(limit).all()

    return jsonify(users=stringify_class(users))
