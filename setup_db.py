# coding=utf-8
from astronet.database import init_db, db_session
from astronet.models import User
from astronet.helpers import gen_filename
from astronet import app

from sqlalchemy.orm.exc import NoResultFound

def setup_db():
        user = User('test@test.com', 'Test User', 'qwerty')
        user.role = 'admin'
        user.activated = True

        db_session.add(user)
        db_session.commit()

if __name__ == '__main__':
    init_db()
    setup_db()
