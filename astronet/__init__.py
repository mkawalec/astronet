# coding=utf-8
from helpers import gen_filename
from flask import jsonify

import user
import posts
import comments
import account

from helpers import auth_required

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

################### Misc API

@app.route('/test')
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

