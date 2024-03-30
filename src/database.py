from enum import unique
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String(80),nullable=False)
    last_name = db.Column(db.String(80),nullable=False)
    username = db.Column(db.String(80),unique=True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    password = db.Column(db.Text,nullable=False)
    avatar = db.Column(db.String(255),nullable=False)
    cover = db.Column(db.String(255))
    bio = db.Column(db.String(100))
    location = db.Column(db.String(120))
    dob = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    followers = db.relationship('Follower', foreign_keys='Follower.followed', backref='user')
    tweets = db.relationship('Tweet',backref='user')
    likes = db.relationship('Like',backref='user')
    retweets = db.relationship('ReTweet',backref='user')
    comments = db.relationship('Comment',backref='user')
    bookmarks = db.relationship('Bookmark',backref='user')
    
    def __repr__(self):
        return f"User ('{self.username}', '{self.email}', '{self.id}')"
    
    def serialize(self):
        return {'id': self.id,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'username': self.username,
                'email': self.email,
                'password': self.password,
                'avatar': self.avatar,
                'cover': self.cover,
                'bio': self.bio,
                'location': self.location,
                'dob': self.dob,
                'created_at': self.created_at,
                'updated_at': self.updated_at}

class Tweet(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False,)
    text = db.Column(db.String(255),nullable=False)
    media = db.Column(db.String(100),nullable=False)
    commentscount = db.Column(db.Integer,default=0)
    retweetscount = db.Column(db.Integer,default=0)
    likescount = db.Column(db.Integer,default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    likes = db.relationship('Like',backref='tweet')
    retweets = db.relationship('ReTweet',backref='tweet')
    bookmarks = db.relationship('Bookmark',backref='tweet')

    def __repr__(self):
        return f"Tweet ({self.text}) ({self.userid})"
    
    def serialize(self):
        return {
            'id': self.id,
            'userid': self.userid,
            'text': self.text,
            'media': self.media,
            'commentscount': self.commentscount,
            'retweetscount': self.retweetscount,
            'likescount': self.likescount,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class ReTweet(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False,)
    tweetid = db.Column(db.Integer,db.ForeignKey('tweet.id'),nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __repr__(self):
        return f"ReTweet ('{self.userid}','{self.tweetid}')"
    
    def serialize(self):
        return {'id': self.id,
                'userid': self.userid,
                'tweetid': self.tweetid,
                'created_at': self.created_at,
                'updated_at': self.updated_at}
    
class Like(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    tweetid = db.Column(db.Integer,db.ForeignKey('tweet.id'),nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __repr__(self):
        return f"Like ('{self.userid}','{self.tweetid}')"
    
    def serialize(self):
        return {'id': self.id,
                'userid': self.userid,
                'tweetid': self.tweetid,
                'created_at': self.created_at,
                'updated_at': self.updated_at}
    
class Follower(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    followed = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    follower = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return f"Follower ('{self.followed}','{self.follower}')"
    
    def serialize(self):
        return {'id': self.id,
                'followed': self.followed,
                'follower': self.follower}

class Comment(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    tweetid = db.Column(db.Integer,nullable=False)
    text = db.Column(db.String(120),nullable=False)
    media = db.Column(db.String(100),nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __repr__(self):
        return f"Comment ('{self.userid}','{self.tweetid}' , '{self.text}')"
    
    def serialize(self):
        return {'id': self.id,
                'userid': self.userid,
                'tweetid': self.tweetid,
                'text': self.text,
                'media': self.media,
                'created_at': self.created_at,
                'updated_at': self.updated_at}

class Bookmark(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    tweetid = db.Column(db.Integer,db.ForeignKey('tweet.id'),nullable=False)

    def __repr__(self):
        return f"Bookmark ('{self.userid}','{self.tweetid}')"
    
    def serialize(self):
        return {
            'id': self.id,
            'userid': self.userid,
            'tweetid': self.tweetid
        }






