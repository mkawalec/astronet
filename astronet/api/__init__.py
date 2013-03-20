# coding=utf-8
from .. import app
from ..helpers import login_required, gen_filename
from ..database import db_session
from ..models import User

from flask import (Blueprint, render_template,
        abort, request, Response, g, jsonify, session)
from functools import wraps

from datetime import datetime, timedelta

from sqlalchemy.orm.exc import NoResultFound

api = Blueprint('api', __name__,
                        template_folder='../templates/api')

def log_in(user):
    """Automatically logging the user """
    session['logged_in'] = True
    session['string_id'] = user.string_id
    session['email'] = user.email
    session['real_name'] = user.real_name
                        
def check_auth(username=None, password=None):
    """ Authentication checker. Works both for browsers autenticating
        with cookies and Basic HTTP Auth requests
    """

    # If the user has a session (ie. is accessing the api
    # through a logged in browser), allow her to proceed
    if 'logged_in' in session:
        if session['logged_in'] == True:
            g.email = session['email']
            g.string_id = session['string_id']
            return True

    # If the API is accessed programmatically, ask about the
    # password
    try:
        user = db_session.query(User).\
                filter(User.email == username).one()
    except NoResultFound:
        return False

    ret = user.check_pass(password)
    if ret:
        log_in(user)
    return ret


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def auth_required(f):
    """ Wrapper for API functions that enforces the need for authentication
        before accessing a method
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # In case session exists 
        if 'logged_in' in session:
            if check_auth():
                return f(*args, **kwargs)

        # If the session doesn't exist
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

from user import *
from posts import *
from comments import *
from account import *

################### Misc API

@api.route('/test')
@auth_required
def test():
    """ A test function that always returns::

            {
                status: 'succ',
                result: 'test'
            }

        .. NOTE:: 
            It is intended to check if you can connect and authenticate 
            with the site properly
    """
    return jsonify(status='succ', result='test')

