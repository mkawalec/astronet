from . import TestCase, new_db
from astronet import app
from flask import url_for

import json

import basic

class UserTests(basic.BasicTests):

    @new_db
    def test_getting(self):
        rv = self.app.get('/user')
        assert rv.status_code == 400

        self.correct_login(not_create=True)

        rv = self.app.get('/user')
        assert rv.status_code == 200

        self.logout(login=False, not_create=True)

        self.standard_login(not_create=True)
        rv = self.app.get('/user')
        assert rv.status_code == 200
       
    @new_db    
    def test_get_users(self):
        rv = self.app.get('/users')
        data = json.loads(rv.data)

        assert len(data['users']) == 2

        rv = self.app.get('/users?after='+data['users'][0]['string_id'])
        data = json.loads(rv.data)
        assert len(data['users']) == 1
        assert data['users'][0]['real_name'] == 'Test User'

        # Test deleting the account
        rv = self.standard_login(not_create=True)
        string_id = json.loads(rv.data)['user']['string_id']
        rv = self.app.delete('/user')
        assert rv.status_code == 200
        
        rv = self.app.get('/test')
        assert rv.status_code == 403

        rv = self.standard_login(not_create=True, test=False)
        assert rv.status_code == 404

        # Test enabling the account
        rv = self.correct_login(not_create=True)
        assert rv.status_code == 200
        
        rv = self.app.post('/user/'+string_id)
        assert rv.status_code == 200

        rv = self.logout(login=False, not_create=True)
        assert rv.status_code == 200

        rv = self.standard_login(not_create=True)
        assert rv.status_code == 200

        rv = self.logout(login=False, not_create=True)
        assert rv.status_code == 200

        # Test changing the account
        rv = self.correct_login(not_create=True)
        assert rv.status_code == 200

        # That that indeed we cannot set the properties
        # that are read_only or invisible
        wrong_props = ['salt', 
                'activated', 'timestamp', 'disabled',
                'edition_timestamp', 'string_id', 'id']
        for prop in wrong_props:
            rv = self.app.put('/user', data={
                prop: 'blah'})
            assert rv.status_code == 409

        # Check if real name can be changed
        rv = self.app.put('/user', data=dict(
            real_name='A changed name'))
        assert rv.status_code == 200

        rv = self.app.get('/user')
        assert json.loads(rv.data)['user']['real_name'] \
                == 'A changed name'

        # Check if the role can be changed by an admin
        rv = self.app.put('/user/'+string_id, data=dict(
            role='admin'))
        assert rv.status_code == 200
        rv = self.app.get('/user/'+string_id)
        assert json.loads(rv.data)['user']['role'] == 'admin'

        rv = self.app.put('/user/'+string_id, data=dict(
            role='user'))
        assert rv.status_code == 200

        # Make sure that the standard user cannot
        # change roles
        self.logout(login=False, not_create=True)
        self.standard_login(not_create=True)
        rv = self.app.put('/user', data=dict(
            role='admin'))
        assert rv.status_code == 409
        rv = self.app.get('/user')
        assert json.loads(rv.data)['user']['role'] == 'user'

        # Check that setting the password works
        rv = self.app.put('/user', data=dict(
            old_password='qwerty',
            password='qwerty1'))
        assert rv.status_code == 200

        self.logout(login=False, not_create=True)
        rv = self.standard_login(not_create=True, password='qwerty1')
        assert rv.status_code == 200

        # Check that wrong password doesn't impact anything
        rv = self.app.put('/user', data=dict(
            old_password='wrong',
            password='new'))
        assert rv.status_code == 403

        # Check that improper param setting attempt fails loudly
        rv = self.app.put('/user', data=dict(
            blah='blah'))
        assert rv.status_code == 400

        # Check that the swapped case password works
        self.logout(login=False, not_create=True)
        self.standard_login(not_create=True, password='QWERTY1')


