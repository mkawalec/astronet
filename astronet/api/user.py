from ..api import api, auth_required
from flask import (request, render_template, g, jsonify, abort)

from ..database import db_session
from ..models import User
from sqlalchemy.orm.exc import NoResultFound

from ..helpers import db_commit

# User name operations
@api.route('/user/name', methods=['GET', 'PUT'])
@api.route('/user/name/<string_id>', methods=['GET', 'PUT'])
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

# Email operations
# TODO: Couple with confirmation codes
'''
@api.route('/user/email', methods=['GET', 'POST'])
@auth_required
def user_email():
    """ Either **GET** s the currently set email or enables the user
        to **POST** a new one
    """
    # Update the email
    if request.method == 'POST':
        ret = query_db('UPDATE users SET email=%s WHERE id=%s',
                       [(request.form['email']).strip(), g.uid])
        if ret == 1:
            return jsonify(status='succ')
        elif ret == -1:
            return jsonify(status='db_constraints_error')
        return jsonify(status='db_error')
    
    # Get the email
    if request.method == 'GET':
        email = query_db('SELECT email FROM users WHERE id=%s',
                         [g.uid], one=True)

        if 'email' not in email:
            return jsonify(status='db_null_error')
        else:
            return jsonify(status='succ', email=email['email'])
'''

# Password change
@api.route('/user/password', methods=['POST'])
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
    
