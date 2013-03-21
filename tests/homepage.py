from . import TestCase, new_db
from astronet import app
from flask import url_for

class HomepageTests(TestCase):

    def test_startup(self):
        rv = self.app.get('/test')
        print rv

