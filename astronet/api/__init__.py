# coding=utf-8
from .. import app
from ..helpers import query_db, login_required, gen_filename
from flask import (Blueprint, render_template,
        abort, request, Response, g, jsonify, session)
from hashlib import sha256
from functools import wraps

from datetime import datetime, timedelta

from psycopg2.extensions import adapt


api = Blueprint('api', __name__,
                        template_folder='../templates/api')

def log_me_in(uid,email,string_id,real_name,role):
    """Automatically logging the user """
    session['logged_in'] = True
    session['uid'] = uid
    session['email'] = email
    session['string_id'] = string_id
    session['real_name'] = real_name
    session['role'] = role
                        
def check_auth(username='', password=''):
    """ Authentication checker. Works both for browsers autenticating
        with cookies and Basic HTTP Auth requests
    """

    # If the user has a session (ie. is accessing the api
    # through a logged in browser), allow her to proceed
    if 'logged_in' in session:
        print True
        if session['logged_in'] == True:
            #TODO tutaj powinno sie dopisac 
            #real_name, string_id etc czy g nie obsuguje tego?
            g.email = session['email']
            g.uid = session['uid']
            return True

    # If the API is accessed programmatically, ask about the
    # password
    passwd = query_db('SELECT passwd FROM users WHERE uname=%s LIMIT 1',
            (username,), one=True)
    if passwd == None:
        return False
    passwd = passwd['passwd']
    
    if passwd == (sha256(password + app.config['SALT']).hexdigest()):
        g.username = username
       #TODO osochodzi? UNAME - nie ma czegoś takiego w bazie?!
        g.uid = query_db('SELECT id FROM users WHERE uname=%s LIMIT 1',
                         (username,), one=True)['id']
        return True
    return False


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

