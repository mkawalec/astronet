from . import app
from flask import (request, render_template, g, jsonify, abort)

from database import db_session
from models import User
from sqlalchemy.orm.exc import NoResultFound

from helpers import db_commit, auth_required

# User name operations
@app.route('/user/name', methods=['GET', 'PUT'])
@app.route('/user/name/<string_id>', methods=['GET', 'PUT'])
@auth_required
def user_name(string_id=None):
    """ If accessed by **GET** returns the user real_name, if known.
        
        If **POST** is used the real name for the currently authenticated
        user is changed. The **POST** ed parameters must be::

            request.form = {
                'real_name': user_real_name
            }
    """
    try:
        if not string_id:
            string_id = g.string_id

        user = db_session.query(User).\
            filter(User.string_id == string_id).one()
    except NoResultFound:
        # No such user exist
        abort(404)

    if request.method == 'PUT':
        user.real_name = request.form['real_name']
        return db_commit()
    
    if request.method == 'GET':
        return jsonify(status='succ', 
                real_name=user.real_name)

# Password change
@app.route('/user/password', methods=['POST'])
@auth_required
def user_password():
    """ Enables the user to change her password """
    user = db_session.query(User).\
            filter(User.string_id == g.string_id).one()

    ret = user.update_pass(request.form['pass_old'],
            request.form['pass1'])
    if ret:
        return db_commit()
    else:
        abort(409)
    
