from flask import jsonify,request
from src.database import *

def get_my_retweets(userid):
    retweets = ReTweet.query.filter_by(userid=userid).all()
    tweet_ids = [retweet.tweetid for retweet in retweets]
    return tweet_ids

def get_my_likes(userid):
    likes = Like.query.filter_by(userid=userid).all()
    tweet_ids = [like.tweetid for like in likes]
    return tweet_ids

def get_liked_tweets(userid):
    liked_tweets = Tweet.query.join(Like).filter(Like.userid == userid).all()
    return [tweet.serialize() for tweet in liked_tweets]

def get_user_tweets(userid):
    user_tweets = Tweet.query.filter_by(userid=userid).all()
    return [tweet.serialize() for tweet in user_tweets]

def get_user_retweets(userid):
    user_retweets = Tweet.query.join(ReTweet).filter(ReTweet.userid == userid).all()
    return [tweet.serialize() for tweet in user_retweets]
