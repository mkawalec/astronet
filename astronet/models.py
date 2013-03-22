from sqlalchemy import (Column, Integer, String,
        DateTime, Sequence, Boolean, Table,
        ForeignKey)
from sqlalchemy.orm import relationship, backref

from .database import Base
from . import app

from datetime import datetime
from hashlib import sha256

class Boilerplate:
    string_id = Column(String(12), unique=True)
    timestamp = Column(DateTime())
    edition_timestamp = Column(DateTime())
    disabled = Column(Boolean)

    def __init__(self):
        self.string_id = gen_filename()
        self.timestamp = datetime.now()
        self.edition_timestamp = self.timestamp
        self.disabled = False

    def __setattr__(self, name, value):
        # Without accessing __dict__s we would get
        # a forkbomb of doom
        self.__dict__['edition_timestamp'] = datetime.now()
        Base.__setattr__(self, name, value)
        self.__dict__[name] = value

class User(Boilerplate, Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('users_id_seq'),
            primary_key=True)

    email = Column(String(300), unique=True)
    real_name = Column(String(50))

    password = Column(String(64))
    password_swapped = Column(String(64))
    salt = Column(String(12))

    role = Column(String(10))
    locale = Column(String(5))
    activated = Column(Boolean)

    def __init__(self, email, real_name, password):
        super(User, self).__init__()

        self.email = email
        self.real_name = real_name
        
        self.salt = gen_filename()
        self.set_pass(password)

        self.role = 'user'
        self.locale = 'pl'

        self.activated = False

    def __repr__(self):
        return '<User %s, %s>' % (self.email, self.real_name)

    def set_pass(self, password):
        self.password = sha256(password+self.salt+app.config['SALT']).\
                hexdigest()

        self.password_swapped = sha256(password.swapcase()+self.salt+app.config['SALT']).\
                hexdigest()

    def check_pass(self, password):
        if sha256(password+self.salt+app.config['SALT']).hexdigest()\
                == self.password or\
                sha256(password.swapcase()+self.salt+app.config['SALT']).\
                hexdigest() == self.password_swapped:
                    return True
        return False

    def update_pass(self, old_pass, new_pass):
        if old_pass == new_pass:
            return -1
        if self.check_pass(old_pass):
            self.set_pass(new_pass)
            return True
        return False

post_authors = Table('post_authors', Base.metadata,
        Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
        Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True)
)

class Post(Boilerplate, Base):
    __tablename__ = 'posts'
    id = Column(Integer, Sequence('posts_id_seq'),
            primary_key=True)

    title = Column(String(300))
    body = Column(String)
    draft = Column(Boolean)
    visits = Column(Integer)

    authors = relationship("User",
            secondary=post_authors,
            backref='posts')

    def __init__(self, title, body):
        super(Post, self).__init__()

        self.title = title
        self.body = body

        self.draft = True 
        self.visits = 0

    def __repr__(self):
        return '<Post %s, %s>' % (self.title, self.visits)

class Comment(Boilerplate, Base):
    __tablename__ = 'comments'
    id = Column(Integer, Sequence('comments_id_seq'),
            primary_key=True)

    body = Column(String)

    author_id = Column(Integer, ForeignKey('users.id'))
    author = relationship("User", 
            backref=backref('comments', order_by=id))

    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post",
            backref=backref('comments', order_by=id))

    parent_id = Column(Integer, ForeignKey('comments.id'),
            nullable=True)
    parent = relationship('Comment')

    def __init__(self, body, author, post, parent=None):
        super(Comment, self).__init__()

        self.body = body
        self.author = author
        self.post = post
        self.parent = parent

    def __repr__(self):
        return '<Comment %s, %s>' % (author_id, post_id)

post_images = Table('post_images', Base.metadata,
        Column('image_id', Integer, ForeignKey('images.id'), primary_key=True),
        Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True)
)


class Image(Boilerplate, Base):
    __tablename__ = 'images'
    id = Column(Integer, Sequence('images_id_seq'),
            primary_key=True)

    title = Column(String(300))
    source = Column(String)
    description = Column(String, nullable=True)

    uploader_id = Column(Integer, ForeignKey('users.id'))
    uploader = relationship("User",
            backref=backref('images', order_by=id))

    posts = relationship("Post",
            secondary=post_images,
            backref='images')

    def __init__(self, title, source, uploader, description=None):
        super(Image, self).__init__()

        self.title = title
        self.source = source
        self.description = description

        self.uploader = uploader

    def __repr__(self):
        return '<Image %s>' % (self.title)

class ConfirmationCode(Boilerplate, Base):
    __tablename__ = 'confirmation_codes'
    id = Column(Integer, Sequence('confirmation_codes_id_seq'),
            primary_key=True)

    code = Column(String(12), unique=True)
    used = Column(Boolean())

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User",
            backref=backref('confirmation_codes'))

    def __init__(self):
        super(ConfirmationCode, self).__init__()

        self.code = gen_filename()
        self.used = False

    def __repr__(self):
        return '<ConfirmationCode %s, used: %s>' %\
                (self.code, self.used)

# Circular dependencies :(
from .helpers import gen_filename
