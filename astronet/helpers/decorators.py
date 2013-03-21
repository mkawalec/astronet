from functools import wraps

from flask import abort, session, g, request, Response
from ..database import db_session
from ..models import User

from flaskext.babel import refresh

from sqlalchemy.orm.exc import NoResultFound

def get_user(f):
    ''' Gets a current user and passes it as a \'user\' parameter
        to the function '''
    @wraps(f)
    def fn(*args, **kwargs):
        try:
            if 'string_id' not in session:
                raise NoResultFound

            user = db_session.query(User).\
                    filter(User.string_id == session['string_id']).one()
        except NoResultFound:
            user = None
        return f(*args, user=user, **kwargs)
    return fn

def get_string_id(f):
    ''' If string_id is not provided tries to get
        string_id of the current user. If it is unavailable,
        a 400 BAD REQUEST is raised. '''
    @wraps(f)
    def fn(*args, **kwargs):
        if 'string_id' not in kwargs:
            if kwargs['user']:
                return f(*args, string_id=kwargs['user'].string_id, **kwargs)
            else:
                abort(400)
        return f(*args, **kwargs)
    return fn

def localize(f):
    @wraps(f)
    def fn(*args, **kwargs):
        g.templang = args[0].user.locale
        refresh()

        return f(*args, **kwargs)
    return fn

def auth_required(f):
    """ Wrapper for API functions that enforces the need for authentication
        before accessing a method
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # In case session exists 
        if 'logged_in' in session:
            return f(*args, **kwargs)

        # If the session doesn't exist
        abort(403)
    return decorated
