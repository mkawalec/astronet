from . import TestCase, new_db
from astronet import app
from flask import url_for

class BasicTests(TestCase):

    def test_startup(self):
        rv = self.app.get('/test')
        assert rv.status_code == 403

    @new_db
    def test_correct_login(self):
        self.app.post('/account/login', data=dict(
            email='admin@test.com',
            password='qwerty'))
        rv = self.app.get('/test')
        assert rv.status_code == 200

    @new_db
    def test_standard_login(self):
        self.app.post('/account/login', data=dict(
            email='user@test.com',
            password='qwerty'))
        rv = self.app.get('/test')
        assert rv.status_code == 200

    @new_db
    def test_incorrect_login(self):
        rv = self.app.post('/account/login', data=dict(
            email='admin@test.com',
            password='wrong_pass'))
        rv2 = self.app.get('/test')
        assert rv.status_code == 403
        assert rv2.status_code == 403
        
        rv = self.app.post('/account/login', data=dict(
            email='wrong@email.com',
            password='wrong_pass'))
        rv2 = self.app.get('/test')
        assert rv.status_code == 404
        assert rv2.status_code == 403
        
    @new_db
    def test_logout(self, login=True):
        if login:
            self.test_correct_login(not_create=True)
        self.app.get('/logout')

        rv = self.app.get('/test')
        assert rv.status_code == 403

    

