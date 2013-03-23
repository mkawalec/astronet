import unittest
import os
os.environ['ASTRONET_SETTINGS'] = 'configs/testing.py'

import astronet 
from astronet.database import init_db
from subprocess import call
from functools import wraps
from setup_db import setup_db

devnull = open('/dev/null', 'w')

class TestCase(unittest.TestCase):

    def setUp(self):
        self.db = astronet.app.config['DB']

        self.app = astronet.app.test_client()
        self.new_db = False

    def tearDown(self):
        astronet.database.db_session.remove()
        astronet.database.engine.dispose()


        if self.new_db:
            call("echo \"update pg_database set datallowconn = 'false' where datname = '%s';"
                 "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '%s';\""
                 "|psql -U postgres" % (self.db, self.db), shell=True, stdout=devnull,
                 stderr=devnull)
            call("echo \'DROP DATABASE %s \'|psql -U postgres" % 
                (self.db), shell=True, stdout=devnull, stderr=devnull)

    def create_db(self):
        call('echo \"CREATE DATABASE %s ENCODING \'UTF8\' TEMPLATE template0\"'
             '|psql -U postgres' % (self.db), shell=True, stdout=devnull,
             stderr=devnull)
        call("cat astronet/sql/*.sql|psql -U postgres -d %s" %
                (self.db), shell=True, stdout=devnull, stderr=devnull)
        astronet.database.rebind()

        init_db()
        setup_db()


### Decorators    
def new_db(f):
    ''' Requests a new database to be created for the test '''

    @wraps(f)
    def create_new(*args, **kwargs):
        if 'not_create' in kwargs and \
                kwargs['not_create']:
                    ''' Sometimes we don't want a new database '''
                    del kwargs['not_create']
                    return f(*args, **kwargs)

        args[0].new_db = True
        TestCase.create_db(args[0])
        return f(*args, **kwargs)
    return create_new

#from users import *
from posts import *
