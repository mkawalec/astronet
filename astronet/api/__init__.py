from .. import app
from ..helpers import query_db, login_required
from flask import (Blueprint, render_template,
        abort, request, Response, g, jsonify, session)
from hashlib import sha256
from functools import wraps

from datetime import datetime, timedelta

from psycopg2.extensions import adapt


api = Blueprint('api', __name__,
                        template_folder='../templates/api')

def check_auth(username='', password=''):
    # If the user has a session (ie. is accessing the api
    # through a logged in browser), allow her to proceed
    if 'logged_in' in session:
        print True
        if session['logged_in'] == True:
            g.email = session['email']
            g.uid = session['uid']
            return True

    # If the API is accessed programmatically, ask about the
    # password
    passwd = query_db('SELECT passwd FROM users WHERE uname=%s',
            [username], one=True)
    if passwd == None:
        return False
    passwd = passwd['passwd']
    
    if passwd == (sha256(password + app.config['SALT']).hexdigest()):
        g.username = username
        g.uid = query_db('SELECT id FROM users WHERE uname=%s',
                         [username], one=True)['id']
        return True
    return False


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def auth_required(f):
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

################### Misc API

@api.route('/test')
@auth_required
def test():
    return jsonify(status='succ', result='test')

