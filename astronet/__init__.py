# coding=utf-8
from __future__ import division
from flask import (Flask, request, redirect, url_for, abort,
        render_template, flash, jsonify, g, session, send_file)

from markdown import markdown

import json
   
app = Flask(__name__)
app.config.from_pyfile('config.cfg')

from .api import api
app.register_blueprint(api, url_prefix='/api')

from helpers import *
from posts import *

@app.route('/')
def home():
    """ Return the homepage template """
    return render_template('home.html')
