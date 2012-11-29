# coding=utf-8
from __future__ import division
from flask import (Flask, request, redirect, url_for, abort,
        render_template, flash, jsonify, g, session, send_file)

from datetime import timedelta
from astronet.helpers import login_required

SECRET_KEY = 'ddsnfkrjoireklfjdslkiro43213213m5,tsrfdeldmfxruc'
SALT = 'nfkren<F4><F4>ffdsdsdfdewdsdfvvv'
PERMANENT_SESSION_LIFETIME = timedelta(days=30)
DB = 'astronet'

   
app = Flask(__name__)

from astronet.api import api
app.register_blueprint(api, url_prefix='/api')

app.config.from_object(__name__)

from helpers import *
from account import *

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_post')
@login_required
def add_post():
    return render_template('add_post.html')
