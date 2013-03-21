from . import app
from flask import (request, render_template, g, jsonify, abort,
        session)

from .database import db_session
from .models import User
from sqlalchemy.orm.exc import NoResultFound

from .helpers import (db_commit, auth_required,
        stringify_class, get_user, get_string_id)

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

@app.route('/user/<string_id>', methods=['PUT', 'DELETE'])
@app.route('/user', methods=['PUT', 'DELETE'])
@get_user
@get_string_id
def set_user_data(user, string_id):
    return 0
