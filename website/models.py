from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Info(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    running = db.Column(db.Boolean,default = False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(150), unique=True)
    password=db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    searches = db.relationship('Search')
    
class Search(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150))
    subreddits = db.Column(db.String(150))
    keywords = db.Column(db.String(150))
    frequency = db.Column(db.String(15))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    posts = db.relationship('Post')
    lastcheck = db.Column(db.DateTime(timezone=True), default = func.now())
    lastemail = db.Column(db.DateTime(timezone=True), default = func.now())

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
    title = db.Column(db.String(150))
    selftext = db.Column(db.String(300))
    date = db.Column(db.String(40))
    realdate = db.Column(db.String(40))
    keyword = db.Column(db.String(150))
    subreddit = db.Column(db.String(150))
    permalink = db.Column(db.String(150))