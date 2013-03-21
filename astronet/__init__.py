# coding=utf-8
from flask import jsonify, Flask

app = Flask(__name__)
app.config.from_object('astronet.configs.default')
app.config.from_envvar('ASTRONET_SETTINGS')

import database
import models

import user
import posts
import comments
import account

from helpers import auth_required

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

