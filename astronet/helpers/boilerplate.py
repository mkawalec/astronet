from .. import app
from flask import g

from ..database import db_session
import pylibmc

@app.before_request
def before_request():
    """ Stuff executed before the request. Sets up the cache """
    g.cache = pylibmc.Client(['127.0.0.1'], binary=True,
            behaviors={'tcp_nodelay': True,
                       'ketama': True})

    g.debug = app.debug


@app.teardown_request
def teardown_request(exception):
    """ Stuff executed at the end of request. Disconnects from the database """
    db_session.remove()
