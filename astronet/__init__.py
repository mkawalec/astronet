# coding=utf-8
from flask import jsonify, Flask
import os

app = Flask(__name__)
app.config.from_object('astronet.configs.default')

if 'ASTRONET_SETTINGS' in os.environ and \
        os.environ['ASTRONET_SETTINGS']:
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

