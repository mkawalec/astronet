from . import app
from helpers import auth_required
from flask import request, g, jsonify, abort, session

from .database import db_session
from .models import User
from sqlalchemy.orm.exc import NoResultFound

@app.route('/account/login', methods=['POST'])
def login():
    try:
        user = db_session.query(User).\
            filter(User.email == request.form['email'].strip()).\
            one()
    except NoResultFound:
        abort(404)

    if user.check_pass(request.form['password']):
        log_in(user)
        return jsonify(status='succ')
    else:
        abort(403)

@app.route('/logout')
@auth_required
def logout():
    if 'logged_in' in session:
        if session['logged_in']:
            del session['logged_in']
            if 'string_id' in session:
                del session['string_id']
            if 'email' in session:
                del session['email']
            if 'real_name' in session:
                del session['real_name']

            return jsonify(status='succ')

    abort(409)

def log_in(user):
    """Automatically logging the user """
    session['logged_in'] = True
    session['string_id'] = user.string_id
    session['email'] = user.email
    session['real_name'] = user.real_name
