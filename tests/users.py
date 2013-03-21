from . import TestCase, new_db
from astronet import app
from flask import url_for

import basic

class UserTests(basic.BasicTests):

    @new_db
    def test_getting(self):
        rv = self.app.get('/user')
        assert rv.status_code == 400

        self.test_correct_login(not_create=True)

        rv = self.app.get('/user')
        assert rv.status_code == 200

        self.test_logout(login=False, not_create=True)

        self.test_standard_login(not_create=True)
        rv = self.app.get('/user')
        assert rv.status_code == 200
        


