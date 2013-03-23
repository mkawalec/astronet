from . import new_db
from astronet import app
from flask import url_for

import json
import basic

class PostTests(basic.BasicTests):
    
    @new_db
    def test_simple(self):
        ''' Tests getting posts with an empty DB '''
        rv = self.app.get('/posts')
        assert rv.status_code == 200
        assert len(json.loads(rv.data)['posts']) == 0

        ''' Check preview generator '''
        rv = self.app.post('/post/preview', data=dict(
            body='test body'))

        ''' We need to authorize first '''
        assert rv.status_code == 403
        self.standard_login(not_create=True)
        rv = self.app.post('/post/preview', data=dict(
            body='test body'))
        assert json.loads(rv.data)['preview'] == u'<p>test body</p>'
        self.logout(login=False, not_create=True)

        ''' So, let's submit a post '''
        ''' We need to login '''
        rv = self.app.post('/post')
        assert rv.status_code == 403
        
        det = self.standard_login(not_create=True)
        string_id = json.loads(det.data)['user']['string_id']
        rv = self.app.post('/post', data=dict(
            title='A test title',
            body='A test body'))
        
        assert rv.status_code == 200

        ''' Get drafts of the current user '''
        rv = self.app.get('/posts?draft=True')
        assert rv.status_code == 200
        posts = json.loads(rv.data)['posts']
        assert len(posts) == 1
        assert posts[0]['body'] == u'<p>A test body</p>'
        assert posts[0]['title'] == u'A test title'
        assert posts[0]['authors'][0]['string_id'] == string_id

        ''' Let's add 10 more posts '''
        for i in range(10):
            rv = self.app.post('/post', data=dict(
                title='A test title',
                body='A test body'))
        rv = self.app.get('/posts?draft=True')
        assert rv.status_code == 200
        posts = json.loads(rv.data)['posts']
        assert len(posts) == 11
        


