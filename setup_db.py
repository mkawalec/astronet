# coding=utf-8
from astronet.database import init_db, db_session
from astronet.models import User
from astronet.helpers import gen_filename
from astronet import app

from sqlalchemy.orm.exc import NoResultFound

def setup_db():
    admin = User('admin@test.com', 'Test Admin', 'qwerty')
    admin.role = 'admin'
    admin.activated = True

    db_session.add(admin)

    user = User('user@test.com', 'Test User', 'qwerty')
    user.activated = True
    db_session.add(user)

    db_session.commit()

if __name__ == '__main__':
    init_db()
    setup_db()
