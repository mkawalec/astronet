# coding=utf-8
from astronet import app
from flask import (g, redirect, url_for, flash, session, request)

from contextlib import closing
import psycopg2
from hashlib import sha256
from base64 import b64encode

from functools import wraps

from random import randint

from glob import glob

from multiprocessing import Process
from subprocess import call

devnull = open('/dev/null', 'w')


def connect_db():
    """ Connect to the database and return the connection object """
    return psycopg2.connect("dbname="+app.config['DB']+" user=postgres port=5433")

def init_db():
    """ Initialises (creates) a database, useful for testing """
    create = Process(target=create_db, args=(app.config['DB'],))
    create.start()
    create.join()

    with closing(connect_db()) as db:
        files = glob('/home/michal/build/startup/srv/srv/sql/*')
        files.sort()
        files = files[1:len(files)]

        for table in files:
            with app.open_resource(table) as f:
                db.cursor().execute(f.read())
                db.commit()

def destroy_db():
    """ Removes the database """
    destroy = Process(target=remove_db, args=(app.config['DB'],))
    destroy.start()
    destroy.join()

def create_db(dbname):
    call("echo \"CREATE DATABASE "+dbname+" ENCODING 'UTF8' "
         "TEMPLATE template0\"|psql -U postgres", 
         stdout=devnull, stderr=devnull, shell=True)

def remove_db(db_name):
    call("echo 'DROP DATABASE "+db_name+"'|psql -U postgres", 
        stdout=devnull, stderr=devnull, shell=True)

@app.before_request
def before_request():
    """ Stuff executed before the request. Sets up the database connection """
    g.db = connect_db()
    g.db.set_client_encoding('UTF8')
    g.db_cursor = g.db.cursor()
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, g.db_cursor)


@app.teardown_request
def teardown_request(exception):
    """ Stuff executed at the end of request. Disconnects from the database """
    g.db_cursor.close()
    g.db.close()


def query_db(query, args=(), one=False):
    """ A database interface proxy. Returns a list of dictionaries
        with dictionary keys corresponding to column names. 

        if *one* is True, only the first result is returned as
        a dictionary (NOT a list having one element)
    """
    cursor = g.db_cursor
    try:
        cursor.execute(query, args)
    except psycopg2.IntegrityError:
        ## Constraints not met
        g.db.rollback()
        return -1

    g.db.commit()

    try:
        rv = [
                dict((cursor.description[idx][0], value)
                 for idx, value in enumerate(row)
                ) for row in cursor.fetchall()]
    except psycopg2.ProgrammingError:
        #print 'Nothing to fetch'
        return 1
    except:
        return 0
    
    return (rv[0] if rv else None) if one else rv

def gen_filename(length=10):
    """ Generates a (rougly) random string of a given length
        consisting of upper and lower case letters and numbers.
        
        The default works well for situations when a reasonable 
        entropy is needed (filenames?)
    """
    filename = ''
    chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
             'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'w', 'x',
             'y', 'q', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
             'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T',
             'U', 'W', 'Q', 'X', 'Y', 'Z', '1', '2', '3', '4', '5',
             '6', '7', '8', '9', '0']
    
    for i in range(length):
        filename += chars[randint(0, len(chars)-1)]
    return filename

## Sends to the client a StringIO object not analysing
## its contents in any way - it will be base64
## encoded before sending
def send_base64(what):
    """ Base64 encodes a file and sends it in http request """
    what.seek(0)
    ret = b64encode(what.getvalue())
    
    headers = {}
    headers['Content-Type'] = 'application/base64'
    
    return Response(ret,headers=headers, mimetype='application/base64', 
            direct_passthrough=True, status='200 OK')


def login_required(f):
    """ Wraps a method so that it can only be ran by an authorized user.
        It is used as follows::
            
            @login_required
            def restricted_function():

        .. NOTE::
            Be aware that it doesn't check if user has any rights to the
            given page, it only checks if she is logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('You must be logged in to access this place', 'info')
            return redirect(url_for('login', next=request.path))
        elif session['logged_in'] == False:
            flash('You must be logged in to access this place', 'info')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def create_query(feed):
    """ Creates a full-text query from user-provided text data in *feed* """
    words = feed.strip().split()
    
    query = ''
    for (i,word) in enumerate(words):
        if len(word) > 2:
            if i != 0 and len(query) > 0:
                query += ' | '
            query += word
    return query

def stringify(results):
    """ Encode all of the results as strings to get rid of non-matching
        datatypes issues
    """
    for result in results:
        for param in result:
            result[param] = unicode(result[param])

    return results

def get_size(bb, sizex, sizey):
    """ Returns a size in pixels of X and Y dimensions of a picture
        such that the picture fits sizex, sizey size constraints and 
        keeps the aspect ratio
    """
    width = bb[2]-bb[0]
    height = bb[3]-bb[1]
    mult = 1

    if width > height:
        mult = sizex/width
        if height*mult > sizey:
            mult = sizey/height*mult
    else:
        mult = sizey/height
        if width*mult > sizex:
            mult = sizex/width*mult

    return (int(width*mult), int(height*mult))
